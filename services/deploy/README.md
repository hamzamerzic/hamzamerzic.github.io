# VPS Deployment (Hetzner)

Deploys IKFast, Robot Link Info, and Mesh Cleaner behind Caddy with automatic
HTTPS, HTTP/2/3, rate limiting, and CORS.

Möbius Launch moved to the org-owned
`mobius-os/mobius-os.github.io` repo. This stack keeps only a legacy
`https://api.hamzamerzic.info/mobius-launch` redirect to `https://mobius.you/`;
it does not build or serve the launcher.

On the shared VPS, this Caddy process also imports the org-owned
`mobius.Caddyfile` fragment so `mobius.you` and `mobius.page` keep working
without duplicating launcher routing in this repo. The launcher itself runs from
the `mobius-os/mobius-os.github.io` repo in a separate `mobius-launch` Compose
project on the external `mobius_edge` Docker network.

## Prerequisites

- Hetzner VPS with Docker and Docker Compose installed
- Domain `api.hamzamerzic.info` pointing to the VPS IP
- SSH access to the VPS
- Org-owned `mobius-os/mobius-os.github.io` checkout available on the same VPS,
  unless `MOBIUS_EDGE_FRAGMENT` points somewhere else

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
# Edit .env with your actual email and allowed origin.

# 3. Build and start
docker network inspect mobius_edge >/dev/null
docker compose up -d --build

# 4. Check logs
docker compose logs -f caddy
```

## Cloudflare DNS

Add an **A record** in Cloudflare:

- **Name:** `api`
- **Content:** `YOUR_VPS_IP`
- **Proxy:** OFF (DNS only / grey cloud) — Caddy handles HTTPS directly.
  If you use Cloudflare proxy (orange cloud), set SSL mode to "Full (strict)".

## What You Get

- **HTTPS** — automatic via Let's Encrypt (Caddy handles renewal)
- **HTTP/2** — enabled by default in Caddy
- **HTTP/3** — enabled via UDP port 443
- **Rate limiting** — 100 requests/min per IP
- **CORS** — only allows requests from your website origin
- **Upload limit** — 256MB
- **Streaming** — IKFast logs stream in real time (`flush_interval -1`)
- **No API keys exposed** — origin-based access control instead

## Updating Services

```bash
cd hamzamerzic.github.io/services/deploy
git pull
docker network inspect mobius_edge >/dev/null
docker compose up -d --build
```

Do not define or build Möbius Launch from this repo. On the shared VPS, update
that service from `mobius-os.github.io/services/deploy` with
`./deploy-shared-vps.sh`, then recreate or reload this Caddy service if the
imported `mobius.Caddyfile` changed.

## Möbius service gateway (`services.mobius.hamzamerzic.info`)

Owner-trusted full web services (Tandoor, Paperless, …) run behind Möbius on
ONE shared browser origin, isolated from the Möbius shell. Each service is a
path (`/services/<slug>`) on this single hostname, so adding a service after
the first needs **no DNS or Caddy change** — only a registry opt-in inside
Möbius.

One-time setup (done 2026-07-16; repeat only on a rebuild from scratch):

1. **DNS** — CNAME `services.mobius` → `mobius.hamzamerzic.info`
   (Cloudflare, DNS only / grey cloud).
2. **Möbius env** — in the mobius checkout's `.env` (the compose env source):
   `MOBIUS_SERVICE_GATEWAY_ORIGIN=https://services.mobius.hamzamerzic.info`,
   then recreate the app container (`scripts/deploy-prod.sh --skip-build`
   from the mobius repo — a plain restart does not re-read compose env).
3. **This Caddy** — the `services.mobius.hamzamerzic.info` site block in
   `Caddyfile` (bare `reverse_proxy mobius:8000`; no header injection — the
   backend owns frame policy and fails closed on non-service paths), then
   `docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile`.
4. **Per service, inside Möbius** — set `"public_surface": true` on the
   service's entry in `/data/local-services.json` and run the actual service
   bound to loopback inside the app container's network namespace. The
   in-product agent does this step.

Verify: `curl https://services.mobius.hamzamerzic.info/api/health` → 404
(fail-closed: the gateway hostname never serves shell/API/recovery), and an
enabled service responds under
`https://services.mobius.hamzamerzic.info/services/<slug>/`.

## Monitoring

```bash
# View logs
docker compose logs -f

# Check service health
curl https://api.hamzamerzic.info/health

# Check resource usage
docker stats
```
