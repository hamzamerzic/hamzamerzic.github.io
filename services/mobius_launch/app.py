import base64
import hashlib
import html
import json
import os
import re
import secrets
import sqlite3
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from contextlib import closing
from datetime import datetime, timezone

from cryptography.fernet import Fernet
from flask import Flask, Response, g, make_response, redirect, render_template_string, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


DATA_DIR = os.environ.get("DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "mobius_launch.sqlite3")
SECRET_PATH = os.path.join(DATA_DIR, "session-secret.txt")
APP_BASE_PATH = os.environ.get("APP_BASE_PATH", "/mobius-launch").rstrip("/")
PUBLIC_BASE_URL = os.environ.get(
    "PUBLIC_BASE_URL", "https://api.hamzamerzic.info/mobius-launch"
).rstrip("/")

RAILWAY_AUTH_URL = os.environ.get(
    "RAILWAY_AUTH_URL", "https://backboard.railway.com/oauth/auth"
)
RAILWAY_TOKEN_URL = os.environ.get(
    "RAILWAY_TOKEN_URL", "https://backboard.railway.com/oauth/token"
)
RAILWAY_ME_URL = os.environ.get(
    "RAILWAY_ME_URL", "https://backboard.railway.com/oauth/me"
)
RAILWAY_GRAPHQL_URL = os.environ.get(
    "RAILWAY_GRAPHQL_URL", "https://backboard.railway.com/graphql/v2"
)
RAILWAY_CLIENT_ID = os.environ.get("RAILWAY_CLIENT_ID", "").strip()
RAILWAY_CLIENT_SECRET = os.environ.get("RAILWAY_CLIENT_SECRET", "").strip()
RAILWAY_REDIRECT_URI = os.environ.get(
    "RAILWAY_REDIRECT_URI", f"{PUBLIC_BASE_URL}/railway/callback"
).strip()
RAILWAY_OAUTH_SCOPES = os.environ.get(
    "RAILWAY_OAUTH_SCOPES", "openid email profile offline_access workspace:member"
).strip()
RAILWAY_TEMPLATE_URL = os.environ.get(
    "RAILWAY_TEMPLATE_URL",
    "https://railway.com/deploy/xVMuX9?referralCode=cERpKq&utm_medium=integration&utm_source=template&utm_campaign=generic",
).strip()
RAILWAY_TEMPLATE_CODE = os.environ.get("RAILWAY_TEMPLATE_CODE", "xVMuX9").strip()
RAILWAY_REFERRAL_CODE = os.environ.get("RAILWAY_REFERRAL_CODE", "cERpKq").strip()
GOOGLE_AUTH_URL = os.environ.get("GOOGLE_AUTH_URL", "https://accounts.google.com/o/oauth2/v2/auth")
GOOGLE_TOKEN_URL = os.environ.get("GOOGLE_TOKEN_URL", "https://oauth2.googleapis.com/token")
GOOGLE_USERINFO_URL = os.environ.get(
    "GOOGLE_USERINFO_URL", "https://openidconnect.googleapis.com/v1/userinfo"
)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_REDIRECT_URI = os.environ.get(
    "GOOGLE_REDIRECT_URI", f"{PUBLIC_BASE_URL}/auth/google/callback"
).strip()
ALLOW_PROTOTYPE_EMAIL_LOGIN = os.environ.get(
    "ALLOW_PROTOTYPE_EMAIL_LOGIN", "true"
).strip().lower() in {"1", "true", "yes", "on"}
MOBIUS_IMAGE_REF = os.environ.get("MOBIUS_IMAGE_REF", "").strip()
MOBIUS_SOURCE_REPO = os.environ.get("MOBIUS_SOURCE_REPO", "mobius-os/mobius").strip()
MOBIUS_SOURCE_BRANCH = os.environ.get("MOBIUS_SOURCE_BRANCH", "main").strip()
MOBIUS_SERVICE_NAME = os.environ.get("MOBIUS_SERVICE_NAME", "mobius").strip()
MOBIUS_SERVICE_PORT = int(os.environ.get("MOBIUS_SERVICE_PORT", "8000"))
MOBIUS_VOLUME_MOUNT_PATH = os.environ.get("MOBIUS_VOLUME_MOUNT_PATH", "/data").strip()
MOBIUS_DEFAULT_VOLUME_SIZE_GB = os.environ.get(
    "MOBIUS_DEFAULT_VOLUME_SIZE_GB",
    os.environ.get("MOBIUS_DEFAULT_VOLUME_SIZE", "2"),
).strip()
MOBIUS_VOLUME_SIZE_OPTIONS_GB = os.environ.get(
    "MOBIUS_VOLUME_SIZE_OPTIONS_GB", "2,5,10,20"
).strip()
MOBIUS_DEPLOY_ENVIRONMENT = os.environ.get("MOBIUS_DEPLOY_ENVIRONMENT", "production").strip()

os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)


class RailwayAPIError(RuntimeError):
    pass


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_secret():
    if os.environ.get("MOBIUS_LAUNCH_SECRET"):
        return os.environ["MOBIUS_LAUNCH_SECRET"]
    if os.path.exists(SECRET_PATH):
        with open(SECRET_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    secret = secrets.token_urlsafe(48)
    with open(SECRET_PATH, "w", encoding="utf-8") as f:
        f.write(secret)
    os.chmod(SECRET_PATH, 0o600)
    return secret


APP_SECRET = load_secret()
SESSION_MAX_AGE = 60 * 60 * 24 * 30  # 30 days; enforced server-side in current_user


def _derive_key(info):
    # Domain-separated key derivation so a leak/bug in one purpose (session
    # forgery) does not also compromise the other (decrypting stored Railway
    # tokens). The info tag makes each derived key independent of the others.
    return hashlib.sha256(APP_SECRET.encode("utf-8") + b"|" + info).digest()


# Timed serializer: the session token itself carries a signed timestamp, so it
# expires server-side (unlike the cookie max_age, which a client can ignore).
serializer = URLSafeTimedSerializer(APP_SECRET, salt="mobius-launch-session")
oauth_state_serializer = URLSafeTimedSerializer(
    APP_SECRET, salt="mobius-launch-railway-oauth"
)
google_state_serializer = URLSafeTimedSerializer(
    APP_SECRET, salt="mobius-launch-google-oauth"
)
fernet = Fernet(base64.urlsafe_b64encode(_derive_key(b"token-encryption")))


def connect_db():
    # WAL + a generous busy_timeout so the request-scoped reader and the
    # background provisioning threads (each on their own connection) don't trip
    # "database is locked" when they contend on the same file.
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("pragma journal_mode=WAL")
    conn.execute("pragma busy_timeout=30000")
    return conn


def db():
    if "db" not in g:
        g.db = connect_db()
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@app.before_request
def csrf_guard():
    # Defense in depth on top of SameSite=Lax cookies: reject any state-changing
    # request the browser marks as coming from another site. Same-origin form
    # posts carry Sec-Fetch-Site: same-origin; a cross-site attack page carries
    # cross-site. Non-browser clients (curl) send no header and pass through.
    # This also closes login-CSRF, since /login is a POST.
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        if request.headers.get("Sec-Fetch-Site") == "cross-site":
            return Response("Forbidden", status=403)


def ensure_column(conn, table, column, ddl):
    rows = conn.execute(f"pragma table_info({table})").fetchall()
    if column not in {row[1] for row in rows}:
        try:
            conn.execute(f"alter table {table} add column {ddl}")
        except sqlite3.OperationalError as exc:
            if "duplicate column name" not in str(exc).lower():
                raise


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.executescript(
            """
            create table if not exists users (
              id text primary key,
              email text not null,
              name text not null,
              avatar_url text,
              auth_provider text not null,
              auth_provider_subject text not null,
              created_at text not null,
              last_login_at text not null
            );

            create table if not exists railway_connections (
              id text primary key,
              user_id text not null,
              railway_sub text,
              railway_email text,
              railway_name text,
              railway_picture text,
              railway_workspace_id text,
              railway_workspace_name text,
              connected_mode text not null,
              granted_scopes text,
              token_type text,
              token_expires_at integer,
              access_token_ciphertext text,
              refresh_token_ciphertext text,
              last_error text,
              created_at text not null,
              updated_at text not null,
              foreign key(user_id) references users(id)
            );

            create table if not exists mobius_instances (
              id text primary key,
              user_id text not null,
              railway_connection_id text,
              display_name text not null,
              handle text not null,
              status text not null,
              railway_project_id text not null,
              railway_environment_id text not null,
              railway_service_id text not null,
              railway_volume_id text not null,
              railway_domain text not null,
              public_url text not null,
              recovery_url text not null,
              auth_mode text not null,
              image_ref text not null,
              source_kind text,
              source_ref text,
              volume_size_gb text,
              railway_project_name text,
              railway_workspace_name text,
              current_step text,
              last_error text,
              last_deployment_id text,
              last_seen_at text,
              created_at text not null,
              updated_at text not null,
              foreign key(user_id) references users(id)
            );

            create table if not exists instance_events (
              id text primary key,
              instance_id text not null,
              level text not null,
              message text not null,
              created_at text not null,
              foreign key(instance_id) references mobius_instances(id)
            );
            """
        )
        ensure_column(conn, "users", "avatar_url", "avatar_url text")
        for column, ddl in [
            ("railway_name", "railway_name text"),
            ("railway_picture", "railway_picture text"),
            ("token_type", "token_type text"),
            ("token_expires_at", "token_expires_at integer"),
            ("access_token_ciphertext", "access_token_ciphertext text"),
            ("refresh_token_ciphertext", "refresh_token_ciphertext text"),
            ("last_error", "last_error text"),
            ("cached_plan", "cached_plan text"),
            ("deploy_blocked", "deploy_blocked text"),
            ("plan_checked_at", "plan_checked_at text"),
        ]:
            ensure_column(conn, "railway_connections", column, ddl)
        for column, ddl in [
            ("source_kind", "source_kind text"),
            ("source_ref", "source_ref text"),
            ("volume_size_gb", "volume_size_gb text"),
            ("tier", "tier text"),
            ("cpu", "cpu text"),
            ("memory_gb", "memory_gb text"),
            ("memory_mb", "memory_mb text"),
            ("plan_label", "plan_label text"),
            ("railway_project_name", "railway_project_name text"),
            ("railway_workspace_name", "railway_workspace_name text"),
            ("current_step", "current_step text"),
            ("last_error", "last_error text"),
            ("last_deployment_id", "last_deployment_id text"),
        ]:
            ensure_column(conn, "mobius_instances", column, ddl)
        conn.commit()


init_db()


def h(value):
    return html.escape(str(value or ""), quote=True)


def path(route=""):
    if not route:
        return APP_BASE_PATH + "/"
    if not route.startswith("/"):
        route = "/" + route
    return APP_BASE_PATH + route


def encrypt_secret(value):
    if not value:
        return None
    return fernet.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value):
    if not value:
        return None
    return fernet.decrypt(value.encode("utf-8")).decode("utf-8")


def google_oauth_configured():
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


def email_login_enabled():
    # The passwordless email fallback is a prototype-only convenience. The
    # moment a real identity provider (Google) is configured we refuse it
    # regardless of the env flag, so the unauthenticated login path cannot be
    # used to impersonate a real account.
    return ALLOW_PROTOTYPE_EMAIL_LOGIN and not google_oauth_configured()


def current_user():
    raw = request.cookies.get("mobius_launch_session")
    if not raw:
        return None
    try:
        payload = serializer.loads(raw, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    user = db().execute(
        "select * from users where id = ?", (payload.get("user_id"),)
    ).fetchone()
    return user


def require_user():
    user = current_user()
    if user is None:
        return None
    return user


def set_session(resp, user_id):
    token = serializer.dumps({"user_id": user_id})
    resp.set_cookie(
        "mobius_launch_session",
        token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=SESSION_MAX_AGE,
        path=APP_BASE_PATH or "/",
    )
    return resp


def clear_session(resp):
    resp.delete_cookie("mobius_launch_session", path=APP_BASE_PATH or "/")
    return resp


def railway_oauth_configured():
    return bool(RAILWAY_CLIENT_ID and RAILWAY_CLIENT_SECRET)


def mobius_source():
    if RAILWAY_TEMPLATE_CODE:
        return "template", RAILWAY_TEMPLATE_CODE
    if MOBIUS_IMAGE_REF:
        return "image", MOBIUS_IMAGE_REF
    return "repo", MOBIUS_SOURCE_REPO


def normalize_handle(value, fallback="mobius"):
    raw = (value or fallback or "mobius").strip().lower()
    raw = re.sub(r"[^a-z0-9-]+", "-", raw)
    raw = re.sub(r"-+", "-", raw).strip("-")
    if len(raw) < 3:
        raw = f"{raw or 'mobius'}-{secrets.token_hex(2)}"
    return raw[:40].strip("-")


def get_connection(user_id):
    return db().execute(
        """
        select * from railway_connections
        where user_id = ?
          and connected_mode = 'oauth'
        order by updated_at desc
        limit 1
        """,
        (user_id,),
    ).fetchone()


def list_instances(user_id):
    return db().execute(
        """
        select * from mobius_instances
        where user_id = ?
          and status != 'deleted'
        order by created_at desc
        """,
        (user_id,),
    ).fetchall()


def short_date(value):
    if not value:
        return "never"
    return str(value).replace("T", " ")[:16]


def coerce_volume_size_gb(value, fallback=None):
    if value is None:
        return fallback
    match = re.search(r"\d+", str(value))
    if not match:
        return fallback
    size = int(match.group(0))
    if size < 1 or size > 100:
        return fallback
    return size


def default_volume_size_gb():
    return coerce_volume_size_gb(MOBIUS_DEFAULT_VOLUME_SIZE_GB, 2) or 2


def volume_size_options_gb():
    default = default_volume_size_gb()
    options = [default]
    for item in re.split(r"[,\s]+", MOBIUS_VOLUME_SIZE_OPTIONS_GB):
        size = coerce_volume_size_gb(item)
        if size and size not in options:
            options.append(size)
    return options


def normalize_volume_size_gb(value):
    size = coerce_volume_size_gb(value)
    options = volume_size_options_gb()
    if size in options:
        return str(size)
    return str(options[0])


def volume_size_mb(value):
    return (coerce_volume_size_gb(value, default_volume_size_gb()) or default_volume_size_gb()) * 1024


def volume_size_label(value):
    size = coerce_volume_size_gb(value, default_volume_size_gb()) or default_volume_size_gb()
    return f"{size} GB"


def volume_size_select_options(selected=None):
    selected_size = normalize_volume_size_gb(selected)
    return "\n".join(
        f"""<option value="{size}" {'selected' if str(size) == selected_size else ''}>{size} GB</option>"""
        for size in volume_size_options_gb()
    )


PLAN_LIMITS = {
    "trial": {
        "max_cpu": 2,
        "max_memory_mb": 512,
        "max_volume_gb": 1,
        "memory_options_mb": [256, 512],
        "volume_options_gb": [1],
    },
    "free": {
        "max_cpu": 1,
        "max_memory_mb": 512,
        "max_volume_gb": 1,
        "memory_options_mb": [256, 512],
        "volume_options_gb": [1],
    },
    "hobby": {
        "max_cpu": 8,
        "max_memory_mb": 8192,
        "max_volume_gb": 5,
        "memory_options_mb": [512, 1024, 2048, 4096, 8192],
        "volume_options_gb": [1, 2, 5],
    },
    "pro": {
        "max_cpu": 32,
        "max_memory_mb": 32768,
        "max_volume_gb": 50,
        "memory_options_mb": [512, 1024, 2048, 4096, 8192, 16384],
        "volume_options_gb": [2, 5, 10, 20, 50],
    },
    "unknown": {
        "max_cpu": 8,
        "max_memory_mb": 8192,
        "max_volume_gb": 5,
        "memory_options_mb": [512, 1024, 2048, 4096],
        "volume_options_gb": [1, 2, 5],
    },
}


def plan_limits(label):
    return PLAN_LIMITS.get(label, PLAN_LIMITS["unknown"])


def plan_default_volume_gb(label):
    return min(2, plan_limits(label)["max_volume_gb"])


def memory_mb_label(value):
    try:
        mb = int(value)
    except (TypeError, ValueError):
        return ""
    if mb < 1024:
        return f"{mb} MB"
    return f"{mb // 1024} GB"


def plan_title(label):
    label = (label or "unknown").lower()
    return label.title() if label in PLAN_LIMITS and label != "unknown" else "Unknown"


def plan_volume_select_options(label, selected=None):
    selected_size = str(selected or plan_default_volume_gb(label))
    return "\n".join(
        f"""<option value="{size}" {'selected' if str(size) == selected_size else ''}>{size} GB</option>"""
        for size in plan_limits(label)["volume_options_gb"]
    )


def plan_memory_select_options(label):
    options = ["""<option value="" selected>Uncapped (up to plan max)</option>"""]
    options.extend(
        f"""<option value="{size}">{memory_mb_label(size)}</option>"""
        for size in plan_limits(label)["memory_options_mb"]
    )
    return "\n".join(options)


def clamped_int(value, fallback, minimum, maximum):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = int(fallback)
    return max(minimum, min(maximum, parsed))


def oauth_error(title, message):
    body = f"""
    <main class="shell narrow">
      <section class="panel">
        <div class="section">
          <div class="brand block">
            <img class="mark" src="https://mobius-os.github.io/mobius-brand.png" alt="">
            <div>
              <h1>{h(title)}</h1>
              <p class="subtitle">{h(message)}</p>
            </div>
          </div>
          <div class="actions left">
            <a class="button primary" href="{path('/')}">Back to Mobius Launch</a>
          </div>
        </div>
      </section>
    </main>
    """
    resp = make_response(render(body), 400)
    resp.delete_cookie("railway_oauth_state", path=APP_BASE_PATH or "/")
    return resp


def compact_api_error(error):
    if isinstance(error, bytes):
        error = error.decode("utf-8", errors="replace")
    try:
        data = json.loads(error)
        if isinstance(data, dict):
            message = data.get("error_description") or data.get("message") or data.get("error")
            if message:
                return str(message)[:360]
            return json.dumps(data)[:360]
    except (TypeError, ValueError):
        pass
    return str(error)[:360]


def upsert_user(email, name, provider, provider_subject, avatar_url=None):
    email = (email or "").strip().lower()
    if not email:
        raise ValueError("email is required")
    timestamp = now_iso()
    existing = db().execute("select * from users where email = ?", (email,)).fetchone()
    if existing:
        db().execute(
            """
            update users
            set name = ?, avatar_url = ?, auth_provider = ?,
                auth_provider_subject = ?, last_login_at = ?
            where id = ?
            """,
            (
                name or existing["name"] or email.split("@", 1)[0],
                avatar_url or existing["avatar_url"],
                provider,
                provider_subject,
                timestamp,
                existing["id"],
            ),
        )
        db().commit()
        return existing["id"]

    user_id = "user_" + uuid.uuid4().hex[:10]
    db().execute(
        """
        insert into users (
          id, email, name, avatar_url, auth_provider, auth_provider_subject,
          created_at, last_login_at
        ) values (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            email,
            name or email.split("@", 1)[0],
            avatar_url,
            provider,
            provider_subject,
            timestamp,
            timestamp,
        ),
    )
    db().commit()
    return user_id


def oauth_form_post(url, data, client_id=None, client_secret=None):
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "mobius-launch/0.1",
    }
    if client_id and client_secret:
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {auth}"
    req = urllib.request.Request(url, data=encoded, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RailwayAPIError(
            f"OAuth request failed ({exc.code}): {compact_api_error(exc.read())}"
        ) from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RailwayAPIError(f"OAuth request failed: {compact_api_error(exc)}") from exc


def railway_form_post(url, data, basic_auth=True):
    if basic_auth:
        return oauth_form_post(
            url,
            data,
            client_id=RAILWAY_CLIENT_ID,
            client_secret=RAILWAY_CLIENT_SECRET,
        )
    return oauth_form_post(url, data)


def railway_get_json(url, access_token):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "mobius-launch/0.1",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RailwayAPIError(
            f"Railway request failed ({exc.code}): {compact_api_error(exc.read())}"
        ) from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RailwayAPIError(f"Railway request failed: {compact_api_error(exc)}") from exc


def railway_graphql(query, access_token, variables=None):
    payload_data = {"query": query}
    if variables is not None:
        payload_data["variables"] = variables
    payload = json.dumps(payload_data).encode("utf-8")
    req = urllib.request.Request(
        RAILWAY_GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "mobius-launch/0.1",
        },
        method="POST",
    )
    if access_token:
        req.add_header("Authorization", f"Bearer {access_token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RailwayAPIError(
            f"Railway request failed ({exc.code}): {compact_api_error(exc.read())}"
        ) from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RailwayAPIError(f"Railway request failed: {compact_api_error(exc)}") from exc
    if data.get("errors"):
        raise RailwayAPIError(compact_api_error(data["errors"]))
    return data.get("data") or {}


def exchange_railway_code(code, redirect_uri, code_verifier):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    if code_verifier:
        data["code_verifier"] = code_verifier
    return railway_form_post(RAILWAY_TOKEN_URL, data)


def fetch_railway_workspaces(access_token):
    data = railway_graphql(
        "query { me { workspaces { id name } } }",
        access_token,
    )
    me = data.get("me") or {}
    return me.get("workspaces") or []


def railway_deploy_blocked(access_token, workspace_id):
    if not workspace_id:
        return None
    try:
        data = railway_graphql(
            "query($id: String!) { resourceAccess(explicitResourceOwner: { type: WORKSPACE, id: $id }) { deployment { disallowed } project { disallowed } } }",
            access_token,
            {"id": workspace_id},
        )
        resource_access = data.get("resourceAccess")
        if not isinstance(resource_access, dict):
            return None
        deployment = resource_access.get("deployment")
        if not isinstance(deployment, dict):
            return None
        reason = deployment.get("disallowed")
        return str(reason) if reason else None
    except (RailwayAPIError, TypeError, ValueError, KeyError):
        return None


def railway_plan_label(access_token, workspace_id):
    if not workspace_id:
        return "unknown"
    try:
        data = railway_graphql(
            "query($id: String!) { workspace(workspaceId: $id) { plan } projects(workspaceId: $id, first: 1) { edges { node { subscriptionType expiredAt } } } }",
            access_token,
            {"id": workspace_id},
        )
        projects = data.get("projects")
        edges = []
        if isinstance(projects, dict):
            edges = projects.get("edges") or []
        if edges:
            node = (edges[0] or {}).get("node") or {}
            label = str(node.get("subscriptionType") or "").lower()
        else:
            workspace = data.get("workspace") or {}
            label = str(workspace.get("plan") or "").lower()
        return label if label in PLAN_LIMITS else "unknown"
    except (RailwayAPIError, TypeError, ValueError, KeyError, IndexError):
        return "unknown"


def save_oauth_connection(user, profile, workspaces, tokens, workspace_error=None):
    timestamp = now_iso()
    workspace = workspaces[0] if workspaces else {}
    existing = get_connection(user["id"])
    refresh_token = tokens.get("refresh_token")
    refresh_ciphertext = (
        encrypt_secret(refresh_token)
        if refresh_token
        else existing["refresh_token_ciphertext"]
        if existing
        else None
    )
    expires_in = int(tokens.get("expires_in") or 3600)
    values = (
        profile.get("sub"),
        profile.get("email") or user["email"],
        profile.get("name"),
        profile.get("picture"),
        workspace.get("id"),
        workspace.get("name"),
        "oauth",
        tokens.get("scope") or RAILWAY_OAUTH_SCOPES,
        tokens.get("token_type") or "Bearer",
        int(time.time()) + expires_in,
        encrypt_secret(tokens.get("access_token")),
        refresh_ciphertext,
        workspace_error,
        timestamp,
    )
    if existing:
        db().execute(
            """
            update railway_connections
            set railway_sub = ?, railway_email = ?, railway_name = ?, railway_picture = ?,
                railway_workspace_id = ?, railway_workspace_name = ?, connected_mode = ?,
                granted_scopes = ?, token_type = ?, token_expires_at = ?,
                access_token_ciphertext = ?, refresh_token_ciphertext = ?,
                last_error = ?, cached_plan = null, deploy_blocked = '', plan_checked_at = null,
                updated_at = ?
            where id = ?
            """,
            values + (existing["id"],),
        )
    else:
        db().execute(
            """
            insert into railway_connections (
              id, user_id, railway_sub, railway_email, railway_name, railway_picture,
              railway_workspace_id, railway_workspace_name, connected_mode, granted_scopes,
              token_type, token_expires_at, access_token_ciphertext,
              refresh_token_ciphertext, last_error, created_at, updated_at
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "rail_" + uuid.uuid4().hex[:10],
                user["id"],
                *values[:-1],
                timestamp,
                timestamp,
            ),
        )
    db().commit()


def refresh_railway_access_token(connection, sql_conn=None):
    expires_at = int(connection["token_expires_at"] or 0)
    access_ciphertext = connection["access_token_ciphertext"]
    if access_ciphertext and expires_at > int(time.time()) + 90:
        return decrypt_secret(access_ciphertext)

    refresh_token = decrypt_secret(connection["refresh_token_ciphertext"])
    if not refresh_token:
        raise RailwayAPIError("Railway access expired. Reconnect Railway to deploy.")

    tokens = railway_form_post(
        RAILWAY_TOKEN_URL,
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    access_token = tokens.get("access_token")
    if not access_token:
        raise RailwayAPIError("Railway did not return a refreshed access token.")

    refresh_ciphertext = encrypt_secret(tokens.get("refresh_token") or refresh_token)
    expires_in = int(tokens.get("expires_in") or 3600)
    params = (
        tokens.get("token_type") or connection["token_type"] or "Bearer",
        int(time.time()) + expires_in,
        encrypt_secret(access_token),
        refresh_ciphertext,
        now_iso(),
        connection["id"],
    )
    target = sql_conn or db()
    target.execute(
        """
        update railway_connections
        set token_type = ?, token_expires_at = ?, access_token_ciphertext = ?,
            refresh_token_ciphertext = ?, updated_at = ?
        where id = ?
        """,
        params,
    )
    target.commit()
    return access_token


def cached_plan_state(connection):
    plan_label = str(connection["cached_plan"] or "unknown").lower()
    if plan_label not in PLAN_LIMITS:
        plan_label = "unknown"
    return {
        "plan_label": plan_label,
        "deploy_blocked": connection["deploy_blocked"] or "",
    }


def plan_cache_fresh(connection):
    checked_at = connection["plan_checked_at"]
    if not checked_at:
        return False
    try:
        checked = datetime.fromisoformat(checked_at)
        if checked.tzinfo is None:
            checked = checked.replace(tzinfo=timezone.utc)
        return time.time() - checked.timestamp() < 300
    except (TypeError, ValueError):
        return False


def get_plan_state(connection):
    if connection is None:
        return {"plan_label": "unknown", "deploy_blocked": ""}
    cached = cached_plan_state(connection)
    if plan_cache_fresh(connection):
        return cached

    try:
        access_token = refresh_railway_access_token(connection)
        workspace_id = connection["railway_workspace_id"]
        plan_label = railway_plan_label(access_token, workspace_id)
        deploy_blocked = railway_deploy_blocked(access_token, workspace_id) or ""
        timestamp = now_iso()
        db().execute(
            """
            update railway_connections
            set cached_plan = ?, deploy_blocked = ?, plan_checked_at = ?, updated_at = ?
            where id = ?
            """,
            (plan_label, deploy_blocked, timestamp, timestamp, connection["id"]),
        )
        db().commit()
        return {"plan_label": plan_label, "deploy_blocked": deploy_blocked}
    except Exception:
        return cached


def add_instance_event(conn, instance_id, level, message):
    conn.execute(
        """
        insert into instance_events (id, instance_id, level, message, created_at)
        values (?, ?, ?, ?, ?)
        """,
        ("evt_" + uuid.uuid4().hex[:12], instance_id, level, message, now_iso()),
    )


def update_instance(conn, instance_id, **fields):
    if not fields:
        return
    fields["updated_at"] = now_iso()
    assignments = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [instance_id]
    conn.execute(
        f"update mobius_instances set {assignments} where id = ?",
        values,
    )
    conn.commit()


def project_environment_id(access_token, project_id):
    data = railway_graphql(
        """
        query project($id: String!) {
          project(id: $id) {
            environments {
              edges {
                node { id name }
              }
            }
          }
        }
        """,
        access_token,
        {"id": project_id},
    )
    edges = (((data.get("project") or {}).get("environments") or {}).get("edges") or [])
    if not edges:
        raise RailwayAPIError("Railway created the project, but no environment was returned.")
    for edge in edges:
        node = edge.get("node") or {}
        if node.get("name") == MOBIUS_DEPLOY_ENVIRONMENT:
            return node.get("id")
    return (edges[0].get("node") or {}).get("id")


def fetch_template(code):
    data = railway_graphql(
        """
        query template($code: String!) {
          template(code: $code) {
            id
            code
            name
            serializedConfig
          }
        }
        """,
        None,
        {"code": code},
    )
    template = data.get("template") or {}
    if not template.get("id") or not template.get("serializedConfig"):
        raise RailwayAPIError(f"Railway template {code} was not found.")
    return template


def template_serialized_config(template, selected_volume_size_gb):
    # Railway returns serializedConfig as a JSON object and templateDeployV2
    # requires the OBJECT back (a stringified copy is a documented failure mode),
    # so we always return a dict, never a JSON string.
    config = template["serializedConfig"]
    if isinstance(config, str):
        try:
            config = json.loads(config)
        except (TypeError, ValueError):
            raise RailwayAPIError("Railway template config was not valid JSON.")
    if not isinstance(config, dict):
        raise RailwayAPIError("Railway template config was not valid JSON.")
    if not selected_volume_size_gb:
        return config

    size_mb = volume_size_mb(selected_volume_size_gb)
    services = config.get("services")
    if isinstance(services, dict):
        for service in services.values():
            if not isinstance(service, dict):
                continue
            mounts = service.get("volumeMounts")
            if not isinstance(mounts, dict):
                continue
            for mount in mounts.values():
                if isinstance(mount, dict) and mount.get("mountPath") in {
                    None,
                    MOBIUS_VOLUME_MOUNT_PATH,
                }:
                    mount["sizeMB"] = size_mb
    return config


def deploy_template(access_token, template, workspace_id, volume_size_gb=None):
    # One-shot deploy: templateDeployV2 with a workspaceId (and no projectId)
    # creates the project, all template services, and the /data volume, AND
    # deploys them, returning {projectId, workflowId}. This replaces the old
    # projectCreate + templateDeployV2 + serviceInstanceDeployV2 sequence, whose
    # trailing deploy just triggered a redundant second build.
    if not workspace_id:
        raise RailwayAPIError(
            "No Railway workspace was found for your account. Reconnect Railway and try again."
        )
    input_data = {
        "templateId": template["id"],
        "serializedConfig": template_serialized_config(template, volume_size_gb),
        "workspaceId": workspace_id,
    }
    data = railway_graphql(
        """
        mutation templateDeployV2($input: TemplateDeployV2Input!) {
          templateDeployV2(input: $input) {
            projectId
            workflowId
          }
        }
        """,
        access_token,
        {"input": input_data},
    )
    payload = data.get("templateDeployV2") or {}
    if not payload.get("projectId"):
        raise RailwayAPIError("Railway did not return a project id after template deploy.")
    return payload


def project_resources(access_token, project_id):
    data = railway_graphql(
        """
        query projectResources($id: String!) {
          project(id: $id) {
            id
            name
            services {
              edges {
                node { id name }
              }
            }
            volumes {
              edges {
                node { id name }
              }
            }
          }
        }
        """,
        access_token,
        {"id": project_id},
    )
    project = data.get("project") or {}
    services = [edge.get("node") or {} for edge in ((project.get("services") or {}).get("edges") or [])]
    volumes = [edge.get("node") or {} for edge in ((project.get("volumes") or {}).get("edges") or [])]
    return project, services, volumes


def wait_for_template_service(access_token, project_id, timeout_seconds=300, on_wait=None):
    # Waits only for the template to REGISTER the service + volume (fast — well
    # before the image finishes building). The build itself is tracked
    # afterwards via the deployment status (see reconcile_deployment_status), so
    # a slow build no longer trips this timeout into a false "error".
    start = time.time()
    last_project = {}
    while time.time() - start < timeout_seconds:
        project, services, volumes = project_resources(access_token, project_id)
        last_project = project
        if services and volumes:
            service = next(
                (s for s in services if s.get("name") == MOBIUS_SERVICE_NAME),
                services[0],
            )
            return project, service, volumes[0]
        if on_wait:
            on_wait(int(time.time() - start))
        time.sleep(3)
    raise RailwayAPIError(
        f"Railway did not register the Mobius service and /data volume within "
        f"{timeout_seconds}s for project {last_project.get('name') or project_id}."
    )


def create_service_domain(access_token, service_id, environment_id):
    data = railway_graphql(
        """
        mutation serviceDomainCreate($input: ServiceDomainCreateInput!) {
          serviceDomainCreate(input: $input) { id domain }
        }
        """,
        access_token,
        {
            "input": {
                "serviceId": service_id,
                "environmentId": environment_id,
                "targetPort": MOBIUS_SERVICE_PORT,
            }
        },
    )
    domain = data.get("serviceDomainCreate") or {}
    if not domain.get("domain"):
        raise RailwayAPIError("Railway did not return a service domain.")
    return domain


def set_service_limits(access_token, environment_id, service_id, cpu, memory_mb):
    containers = {}
    if cpu:
        containers["cpu"] = int(cpu)
    if memory_mb:
        containers["memoryBytes"] = int(memory_mb) * 1024 * 1024
    if not containers:
        return
    patch = {
        "services": {
            service_id: {
                "deploy": {
                    "limitOverride": {
                        "containers": containers
                    }
                }
            }
        }
    }
    railway_graphql(
        """
        mutation environmentPatchCommit($environmentId: String!, $patch: EnvironmentConfig!, $commitMessage: String) {
          environmentPatchCommit(environmentId: $environmentId, patch: $patch, commitMessage: $commitMessage)
        }
        """,
        access_token,
        {
            "environmentId": environment_id,
            "patch": patch,
            "commitMessage": "Set Mobius resource limits",
        },
    )


def latest_deployment(access_token, project_id, service_id, environment_id):
    # The most recent deployment for this service in this environment. status is
    # one of the Railway DeploymentStatus values (INITIALIZING, BUILDING,
    # DEPLOYING, SUCCESS, FAILED, CRASHED, ...). Returns {} if none yet.
    data = railway_graphql(
        """
        query latestDeployment($input: DeploymentListInput!) {
          deployments(input: $input, first: 1) {
            edges { node { id status url createdAt } }
          }
        }
        """,
        access_token,
        {
            "input": {
                "projectId": project_id,
                "serviceId": service_id,
                "environmentId": environment_id,
            }
        },
    )
    edges = ((data.get("deployments") or {}).get("edges") or [])
    return (edges[0].get("node") or {}) if edges else {}


def delete_project(access_token, project_id):
    # Best-effort teardown of a Railway project (used to clean up a failed or
    # unwanted deployment so the user is not billed for an orphan).
    railway_graphql(
        """
        mutation projectDelete($id: String!) {
          projectDelete(id: $id)
        }
        """,
        access_token,
        {"id": project_id},
    )


DEPLOY_STATUS_OK = {"SUCCESS", "SLEEPING"}
DEPLOY_STATUS_BAD = {"FAILED", "CRASHED", "REMOVED", "REMOVING", "SKIPPED"}


def provision_instance(instance_id):
    with closing(connect_db()) as conn:
        project_id = None
        try:
            instance = conn.execute(
                "select * from mobius_instances where id = ?",
                (instance_id,),
            ).fetchone()
            if instance is None:
                return
            connection = conn.execute(
                "select * from railway_connections where id = ?",
                (instance["railway_connection_id"],),
            ).fetchone()
            if connection is None:
                raise RailwayAPIError("Railway is not connected.")

            update_instance(conn, instance_id, status="creating", current_step="Loading Railway template", last_error=None)
            add_instance_event(conn, instance_id, "info", f"Loading Railway template {RAILWAY_TEMPLATE_CODE}")
            access_token = refresh_railway_access_token(connection, conn)
            template = fetch_template(RAILWAY_TEMPLATE_CODE)

            # One call creates the project, service, /data volume, and starts the
            # build (see deploy_template). We then wait for the resources to
            # register and hand off build-progress tracking to the status poll.
            update_instance(conn, instance_id, current_step="Creating your Railway project")
            payload = deploy_template(
                access_token,
                template,
                connection["railway_workspace_id"],
                volume_size_gb=instance["volume_size_gb"],
            )
            project_id = payload["projectId"]
            update_instance(
                conn,
                instance_id,
                railway_project_id=project_id,
                railway_project_name=instance["display_name"],
                railway_workspace_name=connection["railway_workspace_name"],
                last_deployment_id=payload.get("workflowId") or "",
                current_step="Building Mobius (this can take a few minutes)",
            )
            row = conn.execute("select status from mobius_instances where id = ?", (instance_id,)).fetchone()
            if row and row["status"] == "deleted":
                try:
                    delete_project(access_token, project_id)
                except RailwayAPIError:
                    pass
                add_instance_event(conn, instance_id, "info", "Deleted during provisioning; Railway project torn down")
                conn.commit()
                return
            add_instance_event(conn, instance_id, "info", "Railway project created; template deploying")

            def _tick(elapsed):
                update_instance(conn, instance_id, current_step=f"Building Mobius ({elapsed}s)")

            _project, service, volume = wait_for_template_service(
                access_token, project_id, on_wait=_tick
            )
            service_id = service["id"]
            environment_id = project_environment_id(access_token, project_id)
            update_instance(
                conn,
                instance_id,
                railway_service_id=service_id,
                railway_volume_id=volume.get("id") or "",
                railway_environment_id=environment_id,
                current_step="Creating your public link",
            )
            inst_now = conn.execute(
                "select cpu, memory_mb from mobius_instances where id = ?",
                (instance_id,),
            ).fetchone()
            if inst_now and (inst_now["cpu"] or inst_now["memory_mb"]):
                try:
                    set_service_limits(
                        access_token,
                        environment_id,
                        service_id,
                        inst_now["cpu"] or None,
                        inst_now["memory_mb"] or None,
                    )
                    add_instance_event(
                        conn,
                        instance_id,
                        "info",
                        f"Resource caps set: {inst_now['cpu'] or '-'} vCPU / {memory_mb_label(inst_now['memory_mb']) or '-'} RAM",
                    )
                except RailwayAPIError as exc:
                    add_instance_event(
                        conn,
                        instance_id,
                        "info",
                        f"Could not set resource caps (Mobius still deploys): {compact_api_error(exc)}",
                    )
            add_instance_event(
                conn,
                instance_id,
                "info",
                f"Mobius service created with a {volume_size_label(instance['volume_size_gb'])} /data volume",
            )

            row = conn.execute("select status from mobius_instances where id = ?", (instance_id,)).fetchone()
            if row and row["status"] == "deleted":
                try:
                    delete_project(access_token, project_id)
                except RailwayAPIError:
                    pass
                add_instance_event(conn, instance_id, "info", "Deleted during provisioning; Railway project torn down")
                conn.commit()
                return
            domain = create_service_domain(access_token, service_id, environment_id)
            public_url = f"https://{domain['domain']}"
            update_instance(
                conn,
                instance_id,
                railway_domain=domain["domain"],
                public_url=public_url,
                recovery_url=f"{public_url}/recover",
                status="deploying",
                current_step="Railway is building Mobius",
            )
            add_instance_event(conn, instance_id, "info", "Public link created; Railway is building Mobius")
            conn.commit()
        except Exception as exc:
            message = compact_api_error(exc)
            update_instance(
                conn,
                instance_id,
                status="error",
                current_step="Deployment failed",
                last_error=message,
            )
            add_instance_event(conn, instance_id, "error", message)
            if project_id:
                # We do NOT auto-delete: the build may be fine and only a late
                # step (e.g. domain) failed. Surface it so the user can review or
                # Delete the project rather than being silently billed.
                add_instance_event(
                    conn,
                    instance_id,
                    "info",
                    "A Railway project was created before the error. Use Delete to remove it, or review it on Railway.",
                )
            conn.commit()


def reconcile_deployment_status(conn, instance):
    # On demand (called from the status poll): while an instance is "deploying",
    # ask Railway for the latest deployment status and advance it to ready/error.
    # Throttled via last_seen_at so page polling can't hammer the Railway API.
    if instance["status"] != "deploying":
        return instance
    if not (
        instance["railway_project_id"]
        and instance["railway_service_id"]
        and instance["railway_environment_id"]
    ):
        return instance
    if instance["last_seen_at"]:
        try:
            age = time.time() - datetime.fromisoformat(instance["last_seen_at"]).timestamp()
            if age < 8:
                return instance
        except ValueError:
            pass
    connection = conn.execute(
        "select * from railway_connections where id = ?",
        (instance["railway_connection_id"],),
    ).fetchone()
    if connection is None:
        return instance

    fields = {"last_seen_at": now_iso()}
    try:
        access_token = refresh_railway_access_token(connection, conn)
        node = latest_deployment(
            access_token,
            instance["railway_project_id"],
            instance["railway_service_id"],
            instance["railway_environment_id"],
        )
        status = (node.get("status") or "").upper()
        if status in DEPLOY_STATUS_OK:
            fields.update(status="ready", current_step="Ready")
            add_instance_event(conn, instance["id"], "info", "Mobius is live")
        elif status in DEPLOY_STATUS_BAD:
            fields.update(
                status="error",
                current_step="Deployment failed",
                last_error=f"Railway reported the deployment {status.lower()}.",
            )
            add_instance_event(conn, instance["id"], "error", f"Deployment {status.lower()}")
        elif status == "NEEDS_APPROVAL":
            fields.update(current_step="Needs approval in Railway")
        elif status:
            fields.update(current_step=f"Railway: {status.lower()}")
    except RailwayAPIError:
        pass  # transient; try again on the next poll

    update_instance(conn, instance["id"], **fields)
    return conn.execute(
        "select * from mobius_instances where id = ?", (instance["id"],)
    ).fetchone()


def start_provisioning(instance_id):
    thread = threading.Thread(target=provision_instance, args=(instance_id,), daemon=True)
    thread.start()


LAYOUT = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mobius Launch</title>
  <link rel="preconnect" href="https://rsms.me/">
  <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
  <style>
    :root {
      color-scheme: dark;
      --bg: #0d0d0d;
      --surface: #171717;
      --surface2: #212121;
      --border: #2a2a2a;
      --text: #ececec;
      --muted: #a8a8a8;
      --accent: #8b6cf7;
      --accent-dim: #6a4fd1;
      --ok: #63d98c;
      --ok-soft: rgba(99, 217, 140, 0.14);
      --warn: #f2c36b;
      --warn-soft: rgba(242, 195, 107, 0.14);
      --radius: 10px;
    }

    * { box-sizing: border-box; }
    html, body { margin: 0; min-height: 100%; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }
    a { color: inherit; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .shell { max-width: 760px; margin: 0 auto; padding: 28px 20px 64px; }
    .narrow { max-width: 460px; padding-top: 72px; }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 22px;
    }
    .brand { display: flex; align-items: center; gap: 12px; min-width: 0; }
    .brand.block { align-items: flex-start; margin-bottom: 18px; }
    .mark {
      width: 36px;
      height: 36px;
      border-radius: 9px;
      object-fit: cover;
      display: block;
      flex: none;
      filter: drop-shadow(0 4px 14px rgba(139, 108, 247, 0.22));
    }
    h1, h2, h3 { margin: 0; line-height: 1.2; letter-spacing: 0; }
    h1 { font-size: 20px; font-weight: 720; }
    h2 { font-size: 18px; font-weight: 720; }
    h3 { font-size: 15px; font-weight: 680; }
    .subtitle, .hint, .muted { color: var(--muted); }
    .subtitle { margin: 3px 0 0; font-size: 13px; overflow-wrap: anywhere; }
    .hint { margin: 6px 0 0; font-size: 13px; }
    .stack { display: grid; gap: 14px; }
    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
    }
    .section { padding: 20px; }
    .section + .section { border-top: 1px solid var(--border); }
    .section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }
    .hero-panel {
      display: grid;
      align-content: center;
      gap: 18px;
      min-height: 260px;
      padding: 28px;
    }
    .actions { display: flex; align-items: center; justify-content: flex-end; gap: 8px; flex-wrap: wrap; }
    .actions.left { justify-content: flex-start; }
    .button, button {
      appearance: none;
      min-height: 40px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface2);
      color: var(--text);
      padding: 9px 13px;
      font: inherit;
      font-size: 13px;
      font-weight: 650;
      text-decoration: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      white-space: nowrap;
    }
    .button.subtle, button.subtle { background: transparent; color: var(--muted); }
    .button.primary, button.primary {
      background: var(--accent);
      border-color: var(--accent);
      color: #ffffff;
    }
    button:disabled { cursor: not-allowed; opacity: 0.55; }
    .button:hover, button:hover { border-color: var(--accent); text-decoration: none; }
    .button.primary:hover, button.primary:hover { background: var(--accent-dim); }
    .button:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible, summary:focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }
    form { display: grid; gap: 12px; margin: 0; }
    label { display: grid; gap: 6px; color: var(--muted); font-size: 12px; font-weight: 620; }
    input, select {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 8px;
      min-height: 40px;
      padding: 9px 10px;
      font: inherit;
      color: var(--text);
      background: var(--bg);
    }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .tier-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }
    .tier-option { position: relative; }
    .tier-option input {
      position: absolute;
      opacity: 0;
      pointer-events: none;
    }
    .tier-card {
      display: grid;
      gap: 5px;
      height: 100%;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      cursor: pointer;
      background: var(--bg);
      color: var(--muted);
      font-size: 12px;
      font-weight: 620;
    }
    .tier-title {
      color: var(--text);
      font-size: 13px;
      font-weight: 720;
    }
    .tier-blurb, .tier-spec { color: var(--muted); }
    .tier-option input:checked + .tier-card {
      border-color: var(--accent);
      background: var(--surface2);
    }
    .tier-option input:focus-visible + .tier-card {
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }
    .full { grid-column: 1 / -1; }
    .deploy-submit {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }
    details { color: var(--muted); font-size: 13px; }
    summary { cursor: pointer; width: fit-content; }
    details[open] summary { margin-bottom: 10px; }
    .instance-list { display: grid; gap: 12px; }
    .instance {
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--bg);
      padding: 15px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
    }
    .instance details { grid-column: 1 / -1; margin-top: 2px; }
    .url {
      display: inline-block;
      margin-top: 5px;
      color: var(--accent);
      font-size: 13px;
      word-break: break-word;
    }
    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin-top: 11px;
      color: var(--muted);
      font-size: 12px;
    }
    .pill {
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 3px 8px;
      background: var(--surface2);
      color: var(--muted);
      white-space: nowrap;
    }
    .pill.ok { color: var(--ok); background: var(--ok-soft); border-color: rgba(99, 217, 140, 0.25); }
    .pill.warn { color: var(--warn); background: var(--warn-soft); border-color: rgba(242, 195, 107, 0.28); }
    .pill.err { color: #ff9f9f; background: rgba(255, 80, 80, 0.12); border-color: rgba(255, 80, 80, 0.28); }
    .instance-actions { display: flex; gap: 8px; align-items: stretch; justify-content: flex-end; flex-wrap: wrap; min-width: 108px; }
    .command {
      margin-top: 8px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: #0a0a0a;
      color: #e8e3ff;
      padding: 10px 11px;
      font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
      overflow-x: auto;
      white-space: nowrap;
    }
    .notice {
      border: 1px solid rgba(242, 195, 107, 0.28);
      background: var(--warn-soft);
      color: #f5d79a;
      border-radius: 8px;
      padding: 12px 13px;
      font-size: 13px;
    }
    .notice + form { margin-top: 12px; }
    .empty {
      border: 1px dashed var(--border);
      border-radius: 8px;
      padding: 22px;
      color: var(--muted);
      background: var(--bg);
      font-size: 13px;
    }
    .login-copy { margin: 0 0 18px; color: var(--muted); font-size: 14px; }
    .provider-list { display: grid; gap: 10px; margin-bottom: 16px; }
    .divider { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: 12px; margin: 6px 0 2px; }
    .divider::before, .divider::after { content: ""; height: 1px; background: var(--border); flex: 1; }
    .footer-links {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      margin-top: 14px;
      color: var(--muted);
      font-size: 12px;
    }
    .inline-link {
      color: var(--muted);
      font-size: 13px;
    }
    .inline-link:hover { color: var(--text); }
    .advanced {
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--bg);
      padding: 12px;
    }
    .advanced summary {
      color: var(--text);
      font-weight: 650;
    }
    .advanced .form-grid, .advanced .trust-grid { margin-top: 12px; }
    .trust-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .trust-card {
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--bg);
      padding: 14px;
    }
    .trust-card ul {
      margin: 10px 0 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 13px;
    }
    .trust-card li + li { margin-top: 6px; }
    @media (max-width: 860px) {
      .shell { padding: 18px 14px 48px; }
      .narrow { padding-top: 42px; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .actions { justify-content: flex-start; }
      .form-grid { grid-template-columns: 1fr; }
      .tier-grid { grid-template-columns: 1fr; }
      .trust-grid { grid-template-columns: 1fr; }
      .instance { grid-template-columns: 1fr; }
      .instance-actions { min-width: 0; justify-content: flex-start; }
    }
  </style>
</head>
<body>
  {{ body|safe }}
  <script>
    document.addEventListener("click", (event) => {
      const button = event.target.closest("[data-copy]");
      if (!button) return;
      const text = button.getAttribute("data-copy");
      navigator.clipboard.writeText(text).then(() => {
        const old = button.textContent;
        button.textContent = "Copied";
        setTimeout(() => { button.textContent = old; }, 1200);
      });
    });
  </script>
</body>
</html>
"""


def render(body):
    return render_template_string(LAYOUT, body=body)


def brand():
    return """
    <div class="brand">
      <img class="mark" src="https://mobius-os.github.io/mobius-brand.png" alt="">
      <div>
        <h1>Mobius</h1>
        <p class="subtitle">Launch</p>
      </div>
    </div>
    """


def login_page():
    if google_oauth_configured():
        google_button = f"""
          <form method="post" action="{path('/auth/google')}">
            <button class="primary" type="submit">Continue with Google</button>
          </form>
        """
    else:
        google_button = """
          <button class="primary" type="button" disabled>Continue with Google</button>
          <p class="hint">Google OAuth is ready in the app, but this server still needs GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.</p>
        """
    email_fallback = ""
    if email_login_enabled():
        email_fallback = f"""
          <div class="divider">or</div>
          <form method="post" action="{path('/login')}">
            <label>
              Email
              <input type="email" name="email" autocomplete="email" placeholder="you@example.com" required>
            </label>
            <button class="primary" type="submit">Continue</button>
          </form>
        """
    body = f"""
    <main class="shell narrow">
      <section class="panel">
        <div class="section">
          <div class="brand block">
            <img class="mark" src="https://mobius-os.github.io/mobius-brand.png" alt="">
            <div>
              <h1>Mobius Launch</h1>
              <p class="subtitle">Sign in to continue.</p>
            </div>
          </div>
          <div class="provider-list">
            {google_button}
          </div>
          {email_fallback}
        </div>
      </section>
      <nav class="footer-links">
        <a href="{path('/transparency')}">What we store</a>
      </nav>
    </main>
    """
    return render(body)


@app.get("/")
def index():
    user = current_user()
    if user is None:
        return login_page()

    connection = get_connection(user["id"])
    connected = connection is not None
    oauth_ready = railway_oauth_configured()
    workspace = connection["railway_workspace_name"] if connection else ""
    source_kind, source_ref = mobius_source()

    disconnect_action = ""
    if connected:
        disconnect_action = f"""
        <form method="post" action="{path('/railway/disconnect')}">
          <button class="subtle" type="submit">Disconnect</button>
        </form>
        """

    top_status = ""
    if connected:
        top_status = f"""
        <span class="pill ok">{h(workspace or 'Railway connected')}</span>
        {disconnect_action}
        """

    if not connected:
        connection_notice = ""
        if not oauth_ready:
            connection_notice = f"""
            <div class="notice">
              Railway OAuth is wired in the app, but this server still needs RAILWAY_CLIENT_ID and RAILWAY_CLIENT_SECRET.
              <div class="command">{h(RAILWAY_REDIRECT_URI)}</div>
            </div>
            """
        connection_action = """<button class="primary" type="button" disabled>Connect Railway</button>"""
        if oauth_ready:
            connection_action = f"""
              <form method="post" action="{path('/railway/connect')}">
                <button class="primary" type="submit">Connect Railway</button>
              </form>
            """
        body = f"""
        <main class="shell">
          <header class="topbar">
            {brand()}
            <div class="actions">
              <form method="post" action="{path('/logout')}">
                <button class="subtle" type="submit">Sign out</button>
              </form>
            </div>
          </header>
          <div class="stack">
            <section class="panel">
              <div class="hero-panel">
                <div>
                  <h2>Connect Railway</h2>
                  <p class="hint">Mobius Launch creates the Railway project, deploys the official template, attaches storage, and gives you the link.</p>
                </div>
                {connection_notice}
                <div class="actions left">{connection_action}</div>
              </div>
            </section>
            <section class="panel">
              <div class="section">
                <div class="section-title">
                  <div>
                    <h2>Minimal by design</h2>
                    <p class="hint">Railway owns the deployment and billing. Mobius Launch only keeps enough state to reconnect you to what it created.</p>
                  </div>
                </div>
                <div class="meta">
                  <span class="pill">Google identity</span>
                  <span class="pill">Railway token</span>
                  <span class="pill">Deployment links</span>
                  <span class="pill">No app telemetry</span>
                </div>
                <p class="hint"><a class="inline-link" href="{path('/transparency')}">See exactly what is stored</a></p>
              </div>
            </section>
          </div>
          <nav class="footer-links">
            <a href="{path('/transparency')}">What we store</a>
          </nav>
        </main>
        """
        return render(body)

    plan_state = get_plan_state(connection)
    plan_label = plan_state["plan_label"]
    deploy_blocked = plan_state["deploy_blocked"]
    limits = plan_limits(plan_label)
    plan_name = plan_title(plan_label)
    default_volume_gb = plan_default_volume_gb(plan_label)
    instances = list_instances(user["id"])
    rows = []
    for inst in instances:
        project_id = inst["railway_project_id"] or "<pending>"
        ssh = (
            "railway ssh "
            f"--project {project_id} "
            f"--service {MOBIUS_SERVICE_NAME} --environment {MOBIUS_DEPLOY_ENVIRONMENT}"
        )
        status = inst["status"] or "queued"
        pill_class = "ok" if status == "ready" else "err" if status in {"error", "delete_failed"} else "warn"
        open_action = (
            f"""<a class="button primary" href="{h(inst['public_url'])}" target="_blank" rel="noreferrer">Open</a>"""
            if inst["public_url"] and status not in {"error", "delete_failed", "deleted"}
            else """<button type="button" disabled>Open</button>"""
        )
        railway_url = (
            f"https://railway.com/project/{inst['railway_project_id']}"
            if inst["railway_project_id"]
            else ""
        )
        public_link = (
            f"""<a class="url" href="{h(inst['public_url'])}" target="_blank" rel="noreferrer">{h(inst['public_url'])}</a>"""
            if inst["public_url"]
            else f"""<p class="hint">{h(inst['current_step'] or 'Queued')}</p>"""
        )
        home_screen_hint = (
            """<p class="hint">📱 On your phone, open this link and use your browser's Share → "Add to Home Screen" to install Mobius like an app.</p>"""
            if status == "ready" and inst["public_url"]
            else ""
        )
        error_markup = (
            f"""<div class="notice" style="margin-top: 10px;">{h(inst['last_error'])}</div>"""
            if inst["last_error"]
            else ""
        )
        railway_action = (
            f"""<a class="button subtle" href="{h(railway_url)}" target="_blank" rel="noreferrer">View usage &amp; cost on Railway</a>"""
            if railway_url
            else ""
        )
        recovery_action = (
            f"""<a class="button subtle" href="{h(inst['recovery_url'])}" target="_blank" rel="noreferrer">Recovery</a>"""
            if inst["recovery_url"]
            else ""
        )
        delete_action = f"""<form method="post" action="{path('/instances/' + inst['id'] + '/delete')}" onsubmit="return confirm('Delete this Mobius and its Railway project? This cannot be undone.');">
                    <button class="subtle" type="submit">Delete</button>
                  </form>"""
        delete_in_main = status in {"error", "delete_failed"}
        main_delete_action = delete_action if delete_in_main else ""
        advanced_delete_action = "" if delete_in_main else delete_action
        cpu_cap = inst["cpu"] or ""
        memory_cap = inst["memory_mb"] or ""
        if cpu_cap or memory_cap:
            cpu_label = h(cpu_cap) if cpu_cap else "&mdash;"
            memory_label = memory_mb_label(memory_cap)
            memory_label = h(memory_label) if memory_label else "&mdash;"
            caps_pill = f"""<span class="pill">cap: {cpu_label} vCPU / {memory_label}</span>"""
        else:
            caps_pill = """<span class="pill">uncapped</span>"""
        inst_plan = inst["plan_label"] or ""
        plan_pill = (
            f"""<span class="pill">{h(plan_title(inst_plan))} plan</span>"""
            if inst_plan
            else ""
        )
        poll_flag = "1" if status in {"queued", "creating", "deploying"} else "0"
        rows.append(
            f"""
            <article class="instance" data-instance-id="{h(inst['id'])}" data-status="{h(status)}" data-poll="{poll_flag}">
              <div>
                <h3>{h(inst['display_name'])}</h3>
                {public_link}
                {home_screen_hint}
                <div class="meta">
	                  <span class="pill {pill_class}" data-pill>{h(status)}</span>
	                  <span class="pill" data-step>{h(inst['current_step'] or 'created')}</span>
	                  {plan_pill}
	                  {caps_pill}
	                  <span class="pill">{h(volume_size_label(inst['volume_size_gb']))}</span>
	                </div>
	                {error_markup}
	              </div>
	              <div class="instance-actions">
	                {open_action}
	                {main_delete_action}
	              </div>
              <details>
                <summary>Advanced</summary>
                <div class="meta">
                  <span class="pill">{h(inst['handle'])}</span>
                  <span class="pill">created {h(short_date(inst['created_at']))}</span>
                  <span class="pill">{h(inst['source_kind'] or source_kind)}:{h(inst['source_ref'] or inst['image_ref'])}</span>
                </div>
                <div class="command">{h(ssh)}</div>
                <div class="actions left" style="margin-top: 10px;">
	                  <button type="button" data-copy="{h(ssh)}">SSH</button>
	                  {railway_action}
	                  {recovery_action}
	                  {advanced_delete_action}
	                </div>
	              </details>
	            </article>
            """
        )

    instance_markup = "\n".join(rows)

    connection_notice = ""
    if connection and connection["last_error"]:
        connection_notice = f"""
        <div class="notice">{h(connection['last_error'])}</div>
        """

    plan_copy = (
        "We couldn't read your Railway plan - you can still try to deploy."
        if plan_label == "unknown"
        else f"You're on the {plan_name} plan."
    )
    volume_options = plan_volume_select_options(plan_label, default_volume_gb)
    memory_options = plan_memory_select_options(plan_label)
    if deploy_blocked:
        deploy_control = f"""
          <div class="notice">
            <p style="margin: 0 0 10px;">{h(deploy_blocked)}</p>
            <div class="actions left">
              <a class="button primary" href="https://railway.com/account/plans" target="_blank" rel="noreferrer">Manage plan on Railway</a>
              <button type="button" disabled>Deploy Mobius</button>
            </div>
          </div>
        """
    else:
        deploy_control = f"""
          <form method="post" action="{path('/instances')}">
            <div class="form-grid">
              <label class="full">
                Project name
                <input name="display_name" value="My Mobius" maxlength="80" required>
              </label>
            </div>
            <details class="advanced">
              <summary>Advanced</summary>
              <p class="hint">You're on the {h(plan_name)} plan &mdash; up to {limits['max_cpu']} vCPU and {h(memory_mb_label(limits['max_memory_mb']))} RAM per service. Mobius runs uncapped by default; set caps below to limit usage.</p>
              <div class="form-grid">
                <label>
                  Data volume
                  <select name="volume_gb">
                    {volume_options}
                  </select>
                  <span class="hint">Volumes cannot be resized later.</span>
                </label>
                <label>
                  Max CPU (vCPU)
                  <input name="custom_cpu" type="number" min="1" max="{limits['max_cpu']}" placeholder="uncapped">
                </label>
                <label>
                  Max memory
                  <select name="memory_mb">
                    {memory_options}
                  </select>
                </label>
              </div>
            </details>
            <div class="deploy-submit">
              <p class="hint">Runs in the background. When it is ready, open the link and set your Mobius username and password on first visit.</p>
              <button class="primary" type="submit">Deploy Mobius</button>
            </div>
          </form>
        """

    deploy_form = f"""
        <section id="new" class="panel">
          <div class="section">
            <div class="section-title">
              <div>
                <h2>Your Railway plan</h2>
                <p class="hint">{h(plan_copy)}</p>
                <p class="hint">Deploys the official template into {h(workspace or 'your Railway workspace')}.</p>
              </div>
            </div>
            {connection_notice}
            {deploy_control}
          </div>
        </section>
    """

    # Live status: while any instance is still deploying, poll its status
    # endpoint (which reconciles from Railway) so the step advances and the page
    # reloads into the ready/error state without a manual refresh.
    poll_script = """
    <script>
    (function () {
      var base = "__BASE__";
      function poll() {
        document.querySelectorAll('.instance[data-poll="1"]').forEach(function (el) {
          var id = el.getAttribute('data-instance-id');
          fetch(base + '/instances/' + id + '/status', { headers: { 'Accept': 'application/json' } })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (d) {
              if (!d) return;
              var stepEl = el.querySelector('[data-step]');
              if (stepEl && d.current_step) stepEl.textContent = d.current_step;
              if (d.status !== el.getAttribute('data-status')) location.reload();
            })
            .catch(function () {});
        });
      }
      if (document.querySelector('.instance[data-poll="1"]')) setInterval(poll, 5000);
    })();
    </script>
    """.replace("__BASE__", APP_BASE_PATH)

    instances_panel = ""
    if rows:
        instances_panel = f"""
    <section class="panel">
      <div class="section">
        <div class="section-title">
          <h2>Your Mobius</h2>
          <span class="pill">{len(instances)}</span>
        </div>
        <div class="instance-list">{instance_markup}</div>
      </div>
    </section>
    {poll_script}
    """

    main_content = f"{deploy_form}{instances_panel}"

    body = f"""
    <main class="shell">
      <header class="topbar">
        {brand()}
        <div class="actions">
          {top_status}
          <form method="post" action="{path('/logout')}">
            <button class="subtle" type="submit">Sign out</button>
          </form>
        </div>
      </header>
      <div class="stack">{main_content}</div>
      <nav class="footer-links">
        <a href="{path('/transparency')}">What we store</a>
      </nav>
    </main>
    """
    return render(body)


@app.get("/transparency")
def transparency():
    user = current_user()
    back_url = path("/") if user else path("/")
    body = f"""
    <main class="shell">
      <header class="topbar">
        {brand()}
        <div class="actions">
          <a class="button subtle" href="{back_url}">Back</a>
        </div>
      </header>
      <div class="stack">
        <section class="panel">
          <div class="section">
            <div class="section-title">
              <div>
                <h2>What Mobius Launch Stores</h2>
                <p class="hint">The launcher is only a bridge between your Mobius account and your Railway-owned deployments.</p>
              </div>
            </div>
            <div class="trust-grid">
              <div class="trust-card">
                <h3>Stored</h3>
                <ul>
                  <li>Your Mobius Launch account email, name, sign-in provider, and avatar URL when available.</li>
                  <li>An encrypted Railway OAuth token so deployments can be created and refreshed.</li>
                  <li>Deployment metadata: Railway project, service, volume, public URL, chosen auth mode, and volume size.</li>
                  <li>Short provisioning events and errors so failed launches are debuggable.</li>
                </ul>
              </div>
              <div class="trust-card">
                <h3>Not stored</h3>
                <ul>
                  <li>Your Mobius conversations, files, apps, databases, or agent activity.</li>
                  <li>Your Railway password or Google password.</li>
                  <li>Billing data; Railway owns that relationship directly.</li>
                  <li>Product analytics or telemetry from inside your Mobius instance.</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="section">
            <h2>Backend Surface</h2>
            <p class="hint">The minimum backend is an OAuth callback, an encrypted token store, a deploy worker, and a small deployment registry. Open-sourcing this service is the cleanest way to make that claim inspectable.</p>
            <div class="meta">
              <span class="pill">OAuth callbacks</span>
              <span class="pill">Encrypted tokens</span>
              <span class="pill">Template deploy worker</span>
              <span class="pill">Deployment registry</span>
            </div>
          </div>
        </section>
      </div>
    </main>
    """
    return render(body)


@app.post("/login")
def login():
    if not email_login_enabled():
        return redirect(path("/"))
    email = request.form.get("email", "").strip().lower()
    if not email:
        return redirect(path("/"))
    existing = db().execute(
        "select auth_provider from users where email = ?", (email,)
    ).fetchone()
    if existing and existing["auth_provider"] != "prototype-email":
        # Never let the passwordless fallback resolve to an account created via a
        # real provider (e.g. Google) — that would be an account takeover.
        return oauth_error(
            "Use your original sign-in",
            "This email is already registered with a different sign-in method.",
        )
    user_id = upsert_user(
        email=email,
        name=email.split("@", 1)[0],
        provider="prototype-email",
        provider_subject=email,
    )
    resp = make_response(redirect(path("/")))
    return set_session(resp, user_id)


@app.post("/auth/google")
def google_login():
    if not google_oauth_configured():
        return redirect(path("/"))
    state = google_state_serializer.dumps(
        {"nonce": secrets.token_urlsafe(16), "iat": int(time.time())}
    )
    params = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    resp = make_response(redirect(GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)))
    resp.set_cookie(
        "google_oauth_state",
        state,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=10 * 60,
        path=APP_BASE_PATH or "/",
    )
    return resp


@app.get("/auth/google/callback")
def google_callback():
    if request.args.get("error"):
        return oauth_error(
            "Google did not connect",
            request.args.get("error_description") or request.args.get("error"),
        )
    state = request.args.get("state", "")
    cookie_state = request.cookies.get("google_oauth_state", "")
    if not state or not cookie_state or not secrets.compare_digest(state, cookie_state):
        return oauth_error("Google did not connect", "The OAuth state check failed.")
    try:
        google_state_serializer.loads(state, max_age=10 * 60)
    except SignatureExpired:
        return oauth_error("Google did not connect", "The OAuth request expired.")
    except BadSignature:
        return oauth_error("Google did not connect", "The OAuth state was invalid.")

    code = request.args.get("code")
    if not code:
        return oauth_error("Google did not connect", "Google did not return a code.")
    try:
        tokens = oauth_form_post(
            GOOGLE_TOKEN_URL,
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
            },
        )
        access_token = tokens.get("access_token")
        if not access_token:
            raise RailwayAPIError("Google did not return an access token.")
        profile = railway_get_json(GOOGLE_USERINFO_URL, access_token)
        if str(profile.get("email_verified")).lower() not in {"1", "true", "yes"}:
            raise RailwayAPIError("Your Google email address is not verified.")
        email = profile.get("email")
        if not email:
            raise RailwayAPIError("Google did not return an email address.")
        user_id = upsert_user(
            email=email,
            name=profile.get("name") or email.split("@", 1)[0],
            provider="google",
            provider_subject=profile.get("sub") or email,
            avatar_url=profile.get("picture"),
        )
    except RailwayAPIError as exc:
        return oauth_error("Google did not connect", str(exc))

    resp = make_response(redirect(path("/")))
    resp.delete_cookie("google_oauth_state", path=APP_BASE_PATH or "/")
    return set_session(resp, user_id)


@app.post("/logout")
def logout():
    resp = make_response(redirect(path("/")))
    resp.delete_cookie("railway_oauth_state", path=APP_BASE_PATH or "/")
    resp.delete_cookie("google_oauth_state", path=APP_BASE_PATH or "/")
    return clear_session(resp)


@app.post("/railway/connect")
def connect_railway():
    user = require_user()
    if user is None:
        return redirect(path("/"))
    if not railway_oauth_configured():
        return redirect(path("/"))

    code_verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("ascii")).digest()
    ).decode("ascii").rstrip("=")
    state = oauth_state_serializer.dumps(
        {
            "user_id": user["id"],
            "nonce": secrets.token_urlsafe(16),
            "code_verifier": code_verifier,
        }
    )
    params = {
        "response_type": "code",
        "client_id": RAILWAY_CLIENT_ID,
        "redirect_uri": RAILWAY_REDIRECT_URI,
        "scope": RAILWAY_OAUTH_SCOPES,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    if "offline_access" in RAILWAY_OAUTH_SCOPES.split():
        params["prompt"] = "consent"
    if RAILWAY_REFERRAL_CODE:
        params["referralCode"] = RAILWAY_REFERRAL_CODE

    auth_url = RAILWAY_AUTH_URL + "?" + urllib.parse.urlencode(params)
    resp = make_response(redirect(auth_url))
    resp.set_cookie(
        "railway_oauth_state",
        state,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=10 * 60,
        path=APP_BASE_PATH or "/",
    )
    return resp


@app.get("/railway/callback")
def railway_callback():
    user = require_user()
    if user is None:
        return redirect(path("/"))
    if request.args.get("error"):
        return oauth_error(
            "Railway did not connect",
            request.args.get("error_description") or request.args.get("error"),
        )

    state = request.args.get("state", "")
    cookie_state = request.cookies.get("railway_oauth_state", "")
    if not state or not cookie_state or not secrets.compare_digest(state, cookie_state):
        return oauth_error("Railway did not connect", "The OAuth state check failed.")
    try:
        payload = oauth_state_serializer.loads(state, max_age=10 * 60)
    except SignatureExpired:
        return oauth_error("Railway did not connect", "The OAuth request expired.")
    except BadSignature:
        return oauth_error("Railway did not connect", "The OAuth state was invalid.")
    if payload.get("user_id") != user["id"]:
        return oauth_error("Railway did not connect", "The OAuth session user changed.")

    code = request.args.get("code")
    if not code:
        return oauth_error("Railway did not connect", "Railway did not return a code.")

    try:
        tokens = exchange_railway_code(
            code,
            RAILWAY_REDIRECT_URI,
            payload.get("code_verifier"),
        )
        access_token = tokens.get("access_token")
        if not access_token:
            raise RailwayAPIError("Railway did not return an access token.")
        profile = railway_get_json(RAILWAY_ME_URL, access_token)
        workspace_error = None
        try:
            workspaces = fetch_railway_workspaces(access_token)
        except RailwayAPIError as exc:
            workspaces = []
            workspace_error = f"Connected to Railway, but workspace lookup failed: {exc}"
        save_oauth_connection(user, profile, workspaces, tokens, workspace_error)
    except RailwayAPIError as exc:
        return oauth_error("Railway did not connect", str(exc))

    resp = make_response(redirect(path("/")))
    resp.delete_cookie("railway_oauth_state", path=APP_BASE_PATH or "/")
    return resp


@app.post("/railway/disconnect")
def disconnect_railway():
    user = require_user()
    if user is None:
        return redirect(path("/"))
    db().execute("delete from railway_connections where user_id = ?", (user["id"],))
    db().commit()
    return redirect(path("/"))


@app.get("/railway/template")
def railway_template():
    user = require_user()
    if user is None:
        return redirect(path("/"))
    if not RAILWAY_TEMPLATE_URL:
        return redirect(path("/"))
    return redirect(RAILWAY_TEMPLATE_URL)


@app.post("/instances")
def create_instance():
    user = require_user()
    if user is None:
        return redirect(path("/"))
    connection = get_connection(user["id"])
    if connection is None or connection["connected_mode"] != "oauth":
        return redirect(path("/"))

    display_name = (request.form.get("display_name") or "My Mobius").strip()[:80]
    # handle is an internal label only; Railway assigns the real public domain.
    handle = normalize_handle(display_name)
    auth_mode = "local"  # the instance uses its own username/password on first open
    state = get_plan_state(connection)
    if state["deploy_blocked"]:
        return oauth_error("Railway plan required", state["deploy_blocked"])
    limits = plan_limits(state["plan_label"])
    default_volume_gb = plan_default_volume_gb(state["plan_label"])
    volume_gb = coerce_volume_size_gb(request.form.get("volume_gb"), default_volume_gb) or default_volume_gb
    volume_gb = max(1, min(limits["max_volume_gb"], int(volume_gb)))
    custom_cpu_raw = (request.form.get("custom_cpu") or "").strip()
    custom_cpu = (
        None
        if not custom_cpu_raw
        else clamped_int(custom_cpu_raw, limits["max_cpu"], 1, limits["max_cpu"])
    )
    memory_mb_raw = (request.form.get("memory_mb") or "").strip()
    memory_mb = (
        None
        if not memory_mb_raw
        else clamped_int(memory_mb_raw, limits["max_memory_mb"], 128, limits["max_memory_mb"])
    )

    timestamp = now_iso()
    instance_id = "mob_" + uuid.uuid4().hex[:10]
    source_kind, source_ref = mobius_source()
    db().execute(
        """
        insert into mobius_instances (
          id, user_id, railway_connection_id, display_name, handle, status,
          railway_project_id, railway_environment_id, railway_service_id,
          railway_volume_id, railway_domain, public_url, recovery_url,
          auth_mode, image_ref, source_kind, source_ref, volume_size_gb,
          cpu, memory_mb, plan_label, railway_project_name, railway_workspace_name, current_step,
          last_error, last_deployment_id, created_at, updated_at
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            instance_id,
            user["id"],
            connection["id"],
            display_name,
            handle,
            "queued",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            auth_mode,
            source_ref,
            source_kind,
            source_ref,
            str(volume_gb),
            str(custom_cpu) if custom_cpu else "",
            str(memory_mb) if memory_mb else "",
            state["plan_label"],
            display_name,
            connection["railway_workspace_name"],
            "Queued",
            None,
            None,
            timestamp,
            timestamp,
        ),
    )
    add_instance_event(db(), instance_id, "info", "Deployment queued")
    db().commit()
    start_provisioning(instance_id)
    return redirect(path("/#new"), code=303)


@app.get("/instances/<instance_id>/status")
def instance_status(instance_id):
    user = require_user()
    if user is None:
        return Response('{"error":"unauthorized"}', status=401, mimetype="application/json")
    inst = db().execute(
        "select * from mobius_instances where id = ? and user_id = ?",
        (instance_id, user["id"]),
    ).fetchone()
    if inst is None:
        return Response('{"error":"not found"}', status=404, mimetype="application/json")
    inst = reconcile_deployment_status(db(), inst)
    return {
        "id": inst["id"],
        "status": inst["status"],
        "current_step": inst["current_step"],
        "public_url": inst["public_url"],
        "last_error": inst["last_error"],
    }


@app.post("/instances/<instance_id>/delete")
def delete_instance(instance_id):
    user = require_user()
    if user is None:
        return redirect(path("/"))
    inst = db().execute(
        "select * from mobius_instances where id = ? and user_id = ?",
        (instance_id, user["id"]),
    ).fetchone()
    if inst is None:
        return redirect(path("/"))
    if inst["railway_project_id"]:
        connection = db().execute(
            "select * from railway_connections where id = ?",
            (inst["railway_connection_id"],),
        ).fetchone()
        try:
            if connection is None:
                raise RailwayAPIError("Railway is not connected.")
            access_token = refresh_railway_access_token(connection, db())
            delete_project(access_token, inst["railway_project_id"])
        except RailwayAPIError:
            update_instance(
                db(),
                instance_id,
                status="delete_failed",
                current_step="Delete failed",
                last_error="Could not delete the Railway project — try again, or delete it from Railway.",
            )
            add_instance_event(
                db(),
                instance_id,
                "error",
                "Could not delete the Railway project — try again, or delete it from Railway.",
            )
            db().commit()
            return redirect(path("/#new"), code=303)
    update_instance(db(), instance_id, status="deleted", current_step="Deleted")
    add_instance_event(db(), instance_id, "info", "Instance deleted")
    db().commit()
    return redirect(path("/#new"), code=303)


@app.get("/health")
def health():
    return {"status": "ok", "service": "mobius-launch"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
