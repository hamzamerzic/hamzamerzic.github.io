#!/usr/bin/env bash
#
# Build or serve the site in Docker, independent of the host Ruby.
#
# Why Docker: the host Ruby (3.2) does not match the gems vendored under
# vendor/bundle (built for the dev container's Ruby 3.4), and the prebuilt
# al-folio image's bundle is missing gems pinned in our Gemfile.lock
# (e.g. jekyll-terser). Both make a bare `bundle exec jekyll build` fail. This
# script installs the locked gems into a host-cached path the first time
# (~a few minutes, needs network) and reuses it afterwards, so every later
# build is fast and reproducible. imagemagick (responsive images) ships in the
# image, so `_site` matches what GitHub Actions deploys.
#
# Usage:
#   bin/build-local.sh           one-off production build into _site/
#   bin/build-local.sh serve     live-reload dev server at http://localhost:8080
#
set -euo pipefail
cd "$(dirname "$0")/.."

IMAGE="amirpourmand/al-folio:v0.14.4"
BUNDLE_CACHE=".docker-bundle" # host-cached gems (gitignored)
mkdir -p "$BUNDLE_CACHE"

# A root-run build (e.g. a bare `docker compose up`, which runs as root) leaves
# root-owned _site/.jekyll-cache that this --user container then can't write,
# producing a confusing mid-build "Permission denied". Detect and explain it
# rather than fail cryptically.
for d in _site .jekyll-cache; do
  if [ -e "$d" ] && [ ! -w "$d" ]; then
    echo "error: '$d' is not writable by you (likely owned by root from a non-Docker-script build)." >&2
    echo "       run once:  sudo rm -rf _site .jekyll-cache   then retry." >&2
    exit 1
  fi
done

common=(
  --rm
  --user "$(id -u):$(id -g)"
  -e HOME=/tmp
  -e "BUNDLE_PATH=/srv/jekyll/${BUNDLE_CACHE}"
  -v "$PWD":/srv/jekyll
  "$IMAGE"
)

case "${1:-build}" in
  serve)
    docker run -it -p 8080:8080 -p 35729:35729 -e JEKYLL_ENV=development "${common[@]}" \
      bash -lc 'cd /srv/jekyll && bundle install && bundle exec jekyll serve --host=0.0.0.0 --port=8080 --livereload --force_polling'
    ;;
  build)
    docker run -e "JEKYLL_ENV=${JEKYLL_ENV:-production}" "${common[@]}" \
      bash -lc 'cd /srv/jekyll && bundle install && bundle exec jekyll build'
    ;;
  *)
    echo "usage: bin/build-local.sh [build|serve]" >&2
    exit 2
    ;;
esac
