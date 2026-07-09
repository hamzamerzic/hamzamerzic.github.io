# VPS Deployment (Hetzner)

Deploys IKFast, Robot Link Info, Mesh Cleaner, and Mobius Launch behind Caddy with automatic HTTPS, HTTP/2/3, rate limiting, and CORS.

## Prerequisites

- Hetzner VPS with Docker and Docker Compose installed
- Domains `api.hamzamerzic.info`, `mobius.you`, and `mobius.page` pointing to the VPS IP
- SSH access to the VPS

## Initial Server Setup

```bash
# 1. SSH into the VPS
ssh root@YOUR_VPS_IP

# 2. Install Docker (if not already installed)
curl -fsSL https://get.docker.com | sh
apt-get install -y docker-compose-plugin

# 3. Set up firewall (only allow SSH, HTTP, HTTPS)
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp  # HTTP/3
ufw enable

# 4. Create a non-root deploy user
adduser deploy
usermod -aG docker deploy
```

## Deploy

```bash
# 1. Clone the repo on the VPS (or rsync the services/ directory)
git clone https://github.com/hamzamerzic/hamzamerzic.github.io.git
cd hamzamerzic.github.io/services/deploy

# 2. Create .env from the example
cp .env.example .env
# Edit .env with your actual email, domains, and OAuth credentials

# 3. Build and start
docker compose up -d --build

# 4. Check logs
docker compose logs -f caddy
```

## Cloudflare DNS

Add **A records** in Cloudflare:

- **Name:** `api`
- **Content:** `YOUR_VPS_IP`
- **Proxy:** OFF (DNS only / grey cloud) — Caddy handles HTTPS directly.
  If you use Cloudflare proxy (orange cloud), set SSL mode to "Full (strict)".
- **Name:** `mobius.you` / root apex
- **Name:** `mobius.page` / root apex
- **Content:** `YOUR_VPS_IP`
- **Proxy:** OFF unless Cloudflare SSL is set to "Full (strict)".

## Mobius Launch

Mobius Launch is served at both `https://mobius.you` and `https://mobius.page`; neither host redirects to the other. `https://mobius.you` is the canonical URL used in metadata and defaults. The legacy `https://api.hamzamerzic.info/mobius-launch` path redirects to `https://mobius.you`.

Required OAuth callback URLs:

- Google: `https://mobius.you/auth/google/callback`
- Google alternate: `https://mobius.page/auth/google/callback`
- Railway: `https://mobius.you/railway/callback`
- Railway alternate: `https://mobius.page/railway/callback`

Important environment variables:

- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- `RAILWAY_CLIENT_ID` and `RAILWAY_CLIENT_SECRET`
- `RAILWAY_OAUTH_SCOPES=openid email profile offline_access workspace:member`
- `ALLOW_PROTOTYPE_EMAIL_LOGIN=false` once Google sign-in is configured

The launcher stores account/session metadata, encrypted Railway OAuth tokens, deployment records, and provisioning events in the `mobius_launch_data` Docker volume. Back up that volume before moving hosts. It does not store Mobius instance files or chats; those live in the Railway projects it creates.

Operational checks:

```bash
docker compose logs -f mobius-launch
curl https://mobius.page/health
curl https://mobius.you/health
curl https://api.hamzamerzic.info/health
```

If a deployment is interrupted while it is queued or creating, the launcher resumes stale rows on restart. If a Railway project was created before a late failure, the UI leaves the row visible so it can be deleted from the launcher or reviewed in Railway.

## What You Get

- **HTTPS** — automatic via Let's Encrypt (Caddy handles renewal)
- **HTTP/2** — enabled by default in Caddy
- **HTTP/3** — enabled via UDP port 443
- **Rate limiting** — 100 requests/min per IP
- **CORS** — only allows requests from your website origin
- **Upload limit** — 256MB (was 32MB on Cloud Run)
- **Streaming** — IKFast logs stream in real-time (`flush_interval -1`)
- **No API keys exposed** — origin-based access control instead
- **Mobius Launch** — Railway OAuth, plan-aware template deployment, public link creation, and deletion

## Updating Services

```bash
cd hamzamerzic.github.io/services/deploy
git pull
docker compose up -d --build
```

For a launcher-only change:

```bash
docker compose up -d --build mobius-launch caddy
```

## Monitoring

```bash
# View logs
docker compose logs -f

# Check service health
curl https://api.hamzamerzic.info/health

# Check resource usage
docker stats
```
