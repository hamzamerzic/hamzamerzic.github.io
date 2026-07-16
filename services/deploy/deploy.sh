#!/usr/bin/env bash
# Deploy the personal-site API services and install their edge fragment.
# Producer side of the edge contract (see the edge repo's README): join the
# trust-zone network, bring up backends, install the fragment via edgectl.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

EDGE_DIR="${EDGE_DIR:-$HOME/projects/edge}"

docker network inspect edge-personal >/dev/null 2>&1 \
  || docker network create edge-personal >/dev/null

docker compose up -d --build

"$EDGE_DIR/edgectl" install personal api.hamzamerzic.info.Caddyfile

docker compose ps
