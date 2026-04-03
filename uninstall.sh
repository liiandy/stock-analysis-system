#!/bin/bash
#
# 個人理財助理 — Uninstaller
#
# Usage: ./uninstall.sh [--remove-reports]
#

set -e

SKILLS_DIR="$HOME/.claude/skills"
CONFIG_FILE="$HOME/.claude/stock-analysis.conf"
REMOVE_REPORTS=false

if [[ "$1" == "--remove-reports" ]]; then
  REMOVE_REPORTS=true
fi

SKILLS=(
  "stock-orchestrator"
  "stock-data-fetcher"
  "stock-data-validator"
  "stock-financial-analyst"
  "stock-technical-analyst"
  "stock-quant-analyst"
  "stock-industry-macro"
  "stock-news-sentiment"
  "stock-institutional-flow"
  "stock-integrator"
  "stock-dashboard"
)

echo ""
echo "🗑  Uninstalling 個人理財助理..."
echo ""

# Remove skill directories
for skill in "${SKILLS[@]}"; do
  if [ -d "$SKILLS_DIR/$skill" ]; then
    rm -rf "$SKILLS_DIR/$skill"
    echo "   ✓ Removed $skill"
  fi
done

# Remove config
if [ -f "$CONFIG_FILE" ]; then
  rm "$CONFIG_FILE"
  echo "   ✓ Removed config file"
fi

# Optionally remove reports
if [ "$REMOVE_REPORTS" = true ]; then
  OUTPUT_DIR="$HOME/fubon-stock-reports"
  if [ -d "$OUTPUT_DIR" ]; then
    rm -rf "$OUTPUT_DIR"
    echo "   ✓ Removed reports at $OUTPUT_DIR"
  fi
else
  echo ""
  echo "   ℹ  Reports in ~/fubon-stock-reports/ were kept."
  echo "      Use --remove-reports to delete them too."
fi

echo ""
echo "  ✅ Uninstall complete."
echo ""
