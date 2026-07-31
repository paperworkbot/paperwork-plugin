#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
distribution_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
source_dir="$distribution_root/plugins/paperwork/skills"
destination="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)

usage() {
  printf '%s\n' \
    "Usage: $0 [--destination ABSOLUTE_PATH]" \
    "" \
    "Copies Paperwork Agent Skills into OpenCode's global skill directory." \
    "Existing Paperwork skills are moved to timestamped backups."
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --destination)
      [ "$#" -ge 2 ] || {
        usage >&2
        exit 2
      }
      destination=$2
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$destination" in
  /*) ;;
  *)
    printf 'Destination must be an absolute path: %s\n' "$destination" >&2
    exit 2
    ;;
esac

if [ "$destination" = "/" ] || [ "$destination" = "$HOME" ]; then
  printf 'Refusing unsafe destination: %s\n' "$destination" >&2
  exit 2
fi

[ -d "$source_dir" ] || {
  printf 'Skill source is missing: %s\n' "$source_dir" >&2
  exit 1
}

mkdir -p "$destination"

installed=0
for skill in "$source_dir"/*; do
  [ -f "$skill/SKILL.md" ] || continue
  name=$(basename "$skill")
  target="$destination/$name"

  if [ -e "$target" ]; then
    backup="$destination/$name.backup.$timestamp"
    [ ! -e "$backup" ] || {
      printf 'Backup already exists: %s\n' "$backup" >&2
      exit 1
    }
    mv "$target" "$backup"
    printf 'Backed up %s to %s\n' "$name" "$backup"
  fi

  cp -R "$skill" "$target"
  printf 'Installed %s\n' "$name"
  installed=$((installed + 1))
done

[ "$installed" -gt 0 ] || {
  printf 'No skills found in %s\n' "$source_dir" >&2
  exit 1
}

printf 'Installed %s Paperwork skills into %s\n' "$installed" "$destination"
printf '%s\n' \
  "Next: merge opencode.example.jsonc into your OpenCode config and provide" \
  "PAPERWORK_MCP_TOKEN to the OpenCode process without storing it in the file."
