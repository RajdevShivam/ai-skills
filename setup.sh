#!/bin/bash
# Setup ai-skills on a new Linux/VPS machine.
# Run after cloning: bash ~/ai-skills/setup.sh

set -e

SKILLS_DIR="${HOME}/.claude/skills"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$SKILLS_DIR"

for d in "$REPO_DIR"/*/; do
  skill=$(basename "$d")
  ln -sf "$d" "$SKILLS_DIR/$skill"
  echo "linked: $skill"
done

echo "Done. $(ls "$REPO_DIR" | grep -v setup.sh | wc -l) skills linked to $SKILLS_DIR"
