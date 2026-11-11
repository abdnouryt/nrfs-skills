#!/usr/bin/env bash
# NRFS installer — the NR-AI full-stack engineering engine
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="nrfs"

usage() {
  cat <<EOF
NRFS installer — the NR-AI full-stack engineering engine

Usage:
  ./install.sh project            install into this project (./.claude/skills/)
  ./install.sh global             install for all projects (~/.claude/skills/)
  ./install.sh --flat OUTPUT.md   export the whole skill as one markdown file
  ./install.sh --plugin           show the Claude Code plugin install commands

Other agents (Cursor, Windsurf, Cline, Aider, chat models):
  point them at the --flat file, or paste nrfs/SKILL.md into the system prompt.
EOF
}

install_to() {
  local dest="$1"
  mkdir -p "$dest"
  rm -rf "$dest/$SKILL_NAME"
  cp -r "$SRC_DIR/$SKILL_NAME" "$dest/$SKILL_NAME"
  echo "installed: $dest/$SKILL_NAME"
  echo "restart your agent so the skill is picked up, then say: NRFS plan"
}

flat_export() {
  local out="$1"
  : > "$out"
  cat "$SRC_DIR/$SKILL_NAME/SKILL.md" >> "$out"
  for f in "$SRC_DIR/$SKILL_NAME"/references/*.md; do
    printf '\n\n---\n\n' >> "$out"
    cat "$f" >> "$out"
  done
  printf '\n\n---\n\n# Templates (copy when NRFS asks for them)\n\n' >> "$out"
  for f in "$SRC_DIR/$SKILL_NAME"/templates/*; do
    printf '\n### %s\n\n```%s\n' "$(basename "$f")" "$(basename "$f" | sed 's/.*\.//')" >> "$out"
    cat "$f" >> "$out"
    printf '\n```\n' >> "$out"
  done
  echo "flat export: $out"
  echo "point your agent to this file, or paste it into the system prompt."
}

plugin_help() {
  cat <<EOF
Install NRFS as a Claude Code plugin (from the repo root):

  /plugin marketplace add <your-github-user>/<this-repo>
  /plugin install nrfs@nrfs

Or plain skills:

  cp -r nrfs ~/.claude/skills/        # global
  cp -r nrfs .claude/skills/          # this project
EOF
}

case "${1:-}" in
  project)  install_to ".claude/skills" ;;
  global)   install_to "$HOME/.claude/skills" ;;
  --flat)   flat_export "${2:-NRFS-flat.md}" ;;
  --plugin) plugin_help ;;
  --help|-h|*) usage ;;
esac
