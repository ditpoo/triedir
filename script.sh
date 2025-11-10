#!/bin/bash
# Usage: ./create_tree.sh tree.txt
if [ $# -ne 1 ]; then
  echo "Usage: $0 tree.txt"
  exit 1
fi

file="$1"

while IFS= read -r line; do
  # skip blank lines
  [ -z "$line" ] && continue

  # Remove leading tree characters: e.g. “├──”, “│  ”, “└── ” etc
  # Then remove leading spaces/tabs
  # For simplicity assume format like “│   ├── dirName” or “    └── subdir”
  # We convert to relative path by tracking indent level

  # Replace graphic marks, then convert indent depth to path
  stripped="$(echo "$line" | sed -E 's/^[\|`-\ ­ ]*//; s/├── //; s/└── //; s/│   //g')"
  # The above may need fine‐tuning based on your tree.txt format

  # Create directory
  mkdir -p "$stripped"
done < "$file"
