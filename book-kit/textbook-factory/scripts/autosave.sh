#!/bin/bash
# Autosave loop: commit and push everything every N seconds so that a container restart or a
# killed agent cannot lose work.  Start it detached:
#   setsid nohup bash tools/autosave.sh /path/to/repo 600 > /tmp/autosave.log 2>&1 < /dev/null &
# Stop it with:  pkill -f "^bash .*autosave.sh"   (match the exact command, not your own shell)
ROOT="${1:-$(pwd)}"; EVERY="${2:-600}"
cd "$ROOT" || exit 1
while true; do
  sleep "$EVERY"
  if [ -n "$(git status --porcelain)" ]; then
    rm -f .git/index.lock 2>/dev/null
    git add -A >/dev/null 2>&1
    git commit -q -m "WIP: autosave of work in progress" >/dev/null 2>&1 || continue
    git push -q origin HEAD >/dev/null 2>&1
    echo "$(date -u +%H:%M) autosaved $(git log --oneline -1)"
  fi
done
