#!/usr/bin/env bash
# Write backend/.env from environment variables (local or CI).
set -euo pipefail

OUTPUT="${1:-backend/.env}"
mkdir -p "$(dirname "$OUTPUT")"

cat > "$OUTPUT" <<EOF
OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY:-}
GEMINI_API_KEY=${GEMINI_API_KEY:-}
GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.5-flash}
EOF

chmod 600 "$OUTPUT"
echo "Wrote ${OUTPUT}"
