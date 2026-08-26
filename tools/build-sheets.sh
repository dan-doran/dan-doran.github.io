#!/usr/bin/env bash
#
# Renders every sheet in sheets/ to a PDF in pdf/, then checks each is exactly
# one page. The sheets are designed to a fixed 8.5x11in box with an absolutely
# positioned foot, so content that overruns does not visibly collide — it
# silently emits a second page. That is why this script verifies rather than
# just building.
#
# Usage:  ./tools/build-sheets.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME"; exit 1; }

mkdir -p pdf

declare -a SHEETS=(
    "capability:dan-doran-capability-sheet"
    "case-midpoint:dan-doran-case-midpoint"
    "case-filmpac-modernization:dan-doran-case-filmpac-modernization"
    "case-blue-mountain-hay:dan-doran-case-blue-mountain-hay"
    "case-filmpac-data:dan-doran-case-hybrid-data"
    "case-governed-ai:dan-doran-case-governed-ai"
)

fail=0
for entry in "${SHEETS[@]}"; do
    src="${entry%%:*}"
    out="${entry##*:}"
    "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
              --virtual-time-budget=3000 \
              --print-to-pdf="pdf/${out}.pdf" \
              "file://$PWD/sheets/${src}.html" 2>/dev/null

    pages=$(python3 -c "
import re,sys
d=open('pdf/${out}.pdf','rb').read()
print(len(re.findall(rb'/Type\s*/Page[^s]', d)))")

    kb=$(( $(stat -f%z "pdf/${out}.pdf") / 1024 ))
    if [ "$pages" = "1" ]; then
        printf '  ok    %-44s %3s KB\n' "${out}.pdf" "$kb"
    else
        printf '  FAIL  %-44s %s pages — content overruns 11in\n' "${out}.pdf" "$pages"
        fail=1
    fi
done

if [ "$fail" = "1" ]; then
    echo
    echo "Trim copy or reduce section spacing in css/sheet.css, then re-run."
    exit 1
fi

echo
echo "All sheets built to pdf/ and verified at one page."
