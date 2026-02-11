#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python3 scripts/publish_from_cron.py

git add data/latest.json
if ! git diff --cached --quiet; then
  git commit -m "chore: update daily report page data"
  git push origin main
fi
