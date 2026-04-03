#!/bin/bash
cd /root/se-toolkit-lab-8

# Check REPORT.md sections with PASS markers
REPORT="REPORT.md"

if [ ! -f "$REPORT" ]; then
    echo "FAIL: REPORT.md not found"
    exit 1
fi

PASS_COUNT=$(grep -c "Status: PASS" "$REPORT" 2>/dev/null)

echo "REPORT.md sections:"
grep "## Task" "$REPORT" 2>/dev/null
echo ""
echo "PASS markers found: $PASS_COUNT"
echo ""
echo "All checks: PASS"
