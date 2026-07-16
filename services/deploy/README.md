# Personal-site API services (VPS)

The backends behind `https://api.hamzamerzic.info`: IKFast solver
generation, Robot Link Info, and Mesh Cleaner.

This directory owns ONLY the personal-site services and their routing
fragment. TLS termination and ports 80/443 belong to the host's shared
edge proxy (the `edge` repo at `~/projects/edge` on the VPS) — this repo
installs `api.hamzamerzic.info.Caddyfile` into it and never runs a proxy
of its own. Möbius routing lives in the Möbius repos; nothing about it is
defined here.

## Deploy

```bash
git clone https://github.com/hamzamerzic/hamzamerzic.github.io.git
cd hamzamerzic.github.io/services/deploy
./deploy.sh          # compose up + edgectl install + reload
```

`deploy.sh` assumes the edge checkout at `~/projects/edge` (override with
`EDGE_DIR=...`). The edge proxy enforces per-producer hostname ownership,
validates the assembled config before reload, and keeps the previous
fragment on any failure.

## What the fragment provides

- **HTTPS/HTTP2/HTTP3, certificates** — the edge proxy's job
- **Rate limiting** — 100 requests/min per IP
- **CORS + origin check** — only `https://hamzamerzic.info` may call the
  API routes from a browser; no-Origin clients (curl) pass
- **Upload limit** — 256MB
- **Streaming** — IKFast logs stream in real time (`flush_interval -1`)
- **Legacy redirect** — `/mobius-launch*` → `https://mobius.you/` (the
  launcher moved to `mobius-os/mobius-os.github.io`)

## Updating

```bash
cd hamzamerzic.github.io/services/deploy
git pull
./deploy.sh
```

## Monitoring

```bash
docker compose ps
docker compose logs -f
curl https://api.hamzamerzic.info/health
```
