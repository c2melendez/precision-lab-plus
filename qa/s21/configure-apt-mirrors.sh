#!/usr/bin/env bash
set -euo pipefail

# Runner images can also select mirrors through mirror+file and apt-mirrors.txt.
sources_dir=${1:-/etc/apt}
while IFS= read -r -d '' source_file; do
  sed -i -E 's|https?://azure\.archive\.ubuntu\.com/ubuntu|https://archive.ubuntu.com/ubuntu|g' "$source_file"
  if grep -Eq 'https?://azure\.archive\.ubuntu\.com/ubuntu' "$source_file"; then
    echo "Azure Ubuntu mirror still active in $source_file" >&2
    exit 1
  fi
done < <(find "$sources_dir" -maxdepth 2 -type f \( -name '*.list' -o -name '*.sources' -o -name '*mirrors*.txt' \) -print0)
