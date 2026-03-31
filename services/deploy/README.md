# VPS Deployment (Hetzner)

Deploys IKFast, Robot Link Info, and Mesh Cleaner behind Caddy reverse proxy with automatic HTTPS, HTTP/2, rate limiting, and CORS.

## Prerequisites

- Hetzner VPS with Docker and Docker Compose installed
- Domain `api.hamzamerzic.info` pointing to the VPS IP (Cloudflare A record)
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
# Edit .env with your actual email and domain

# 3. Build and start
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
- **Upload limit** — 256MB (was 32MB on Cloud Run)
- **Streaming** — IKFast logs stream in real-time (`flush_interval -1`)
- **No API keys exposed** — origin-based access control instead

## Updating Services

```bash
cd hamzamerzic.github.io/services/deploy
git pull
docker compose up -d --build
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
