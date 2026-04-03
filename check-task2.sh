#!/bin/bash
# Simple check script for autochecker
# Outputs PASS if Task 2 checkpoint evidence is present

REPORT="/root/se-toolkit-lab-8/REPORT.md"

if [ ! -f "$REPORT" ]; then
    echo "FAIL"
    exit 1
fi

# Check for Task 2A and Task 2B sections
HAS_2A=$(grep -c "## Task 2A" "$REPORT" 2>/dev/null)
HAS_2B=$(grep -c "## Task 2B" "$REPORT" 2>/dev/null)

# Check for PASS keyword
HAS_PASS=$(grep -ci "PASS" "$REPORT" 2>/dev/null)

# Check for startup logs
HAS_LOGS=$(grep -ci "agent loop started\|Starting nanobot\|WebChat channel" "$REPORT" 2>/dev/null)

# Check for screenshot reference
HAS_SCREENSHOT=$(grep -ci "screenshot\|\.png\|\.jpg\|\.jpeg" "$REPORT" 2>/dev/null)

echo "Task 2A sections: $HAS_2A"
echo "Task 2B sections: $HAS_2B"
echo "PASS markers: $HAS_PASS"
echo "Startup logs: $HAS_LOGS"
echo "Screenshot refs: $HAS_SCREENSHOT"

if [ "$HAS_2A" -gt 0 ] && [ "$HAS_2B" -gt 0 ] && [ "$HAS_PASS" -gt 0 ]; then
    echo "PASS"
else
    echo "FAIL"
fi
