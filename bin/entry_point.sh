#!/bin/bash
set -euo pipefail

echo "🚀 Starting Mesh Cleaner Jekyll dev environment..."

CONFIG_FILE="_config.yml"
JEKYLL_PID=""

# Safe Git settings (for Codespaces)
git config --global --add safe.directory '*'

# Clean or restore Gemfile.lock if needed
if [ -f Gemfile.lock ]; then
  if git ls-files --error-unmatch Gemfile.lock &> /dev/null; then
    echo "🔒 Keeping tracked Gemfile.lock"
    git restore Gemfile.lock || true
  else
    echo "🧹 Removing untracked Gemfile.lock"
    rm -f Gemfile.lock
  fi
fi

# Function to start Jekyll server
start_jekyll() {
  echo "💎 Starting Jekyll server with live reload..."
  bundle exec jekyll serve \
    --host=0.0.0.0 \
    --port=8080 \
    --livereload \
    --trace \
    --force_polling &
  JEKYLL_PID=$!
}

# Function to kill Jekyll if running
stop_jekyll() {
  if [ -n "$JEKYLL_PID" ] && kill -0 $JEKYLL_PID 2>/dev/null; then
    echo "🛑 Restarting Jekyll server due to config change..."
    kill -9 $JEKYLL_PID
    wait $JEKYLL_PID 2>/dev/null || true
  fi
}

# Start initial Jekyll process
start_jekyll

# Watch for changes to _config.yml using inotify
while inotifywait -e modify "$CONFIG_FILE"; do
  stop_jekyll
  start_jekyll
done
