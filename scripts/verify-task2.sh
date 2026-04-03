#!/bin/bash
# Task 2 Verification Script
# Run via SSH: ssh root@<vm-ip> ~/se-toolkit-lab-8/scripts/verify-task2.sh
set -e

echo "============================================================"
echo "TASK 2 VERIFICATION — Deployed Web Client"
echo "============================================================"
PASS=true

# 1. Check Docker containers are running
echo ""
echo "1. Checking Docker containers..."
CONTAINERS_UP=$(docker compose -f /root/se-toolkit-lab-8/docker-compose.yml --env-file /root/se-toolkit-lab-8/.env.docker.secret ps --format json 2>/dev/null | python3 -c "
import sys, json
count = 0
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        obj = json.loads(line)
        if 'running' in obj.get('State', '').lower() or 'Running' in obj.get('State', ''):
            count += 1
    except: pass
print(count)
" 2>/dev/null || echo "0")

if [ "$CONTAINERS_UP" -ge 4 ] 2>/dev/null; then
    echo "   ✅ $CONTAINERS_UP containers running"
else
    echo "   ⚠️  Container count: $CONTAINERS_UP (expected >= 4)"
fi

# 2. Check Flutter web client
echo ""
echo "2. Checking Flutter web client at /flutter..."
FLUTTER_CHECK=$(curl -s --max-time 5 http://localhost:42002/flutter/ 2>/dev/null | grep -c "Nanobot" || echo "0")
JS_CHECK=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:42002/flutter/main.dart.js 2>/dev/null || echo "000")

if [ "$FLUTTER_CHECK" -gt 0 ] 2>/dev/null && [ "$JS_CHECK" = "200" ]; then
    echo "   ✅ Flutter web client served — Nanobot found in HTML, main.dart.js OK (HTTP $JS_CHECK)"
else
    echo "   ❌ Flutter check: Nanobot=$FLUTTER_CHECK, JS=$JS_CHECK"
    PASS=false
fi

# 3. Check nanobot logs for PASS indicators
echo ""
echo "3. Checking nanobot service..."
NANOBOT_LOGS=$(docker compose -f /root/se-toolkit-lab-8/docker-compose.yml --env-file /root/se-toolkit-lab-8/.env.docker.secret logs nanobot 2>&1 | tail -50)

if echo "$NANOBOT_LOGS" | grep -qi "Agent loop started"; then
    echo "   ✅ Agent loop started"
else
    echo "   ❌ Agent loop not found in logs"
    PASS=false
fi

if echo "$NANOBOT_LOGS" | grep -qi "WebChat channel enabled\|webchat channel\|Channels enabled.*webchat\|webchat"; then
    echo "   ✅ WebChat channel enabled"
else
    echo "   ❌ WebChat channel not found in logs"
    PASS=false
fi

if echo "$NANOBOT_LOGS" | grep -qi "MCP server.*connected"; then
    echo "   ✅ MCP servers connected"
else
    echo "   ❌ MCP connections not found in logs"
    PASS=false
fi

# 4. Check REPORT.md has PASS markers
echo ""
echo "4. Checking REPORT.md evidence..."
REPORT="/root/se-toolkit-lab-8/REPORT.md"
if [ -f "$REPORT" ]; then
    TASK2A_PASS=$(grep -c -i "PASS" "$REPORT" 2>/dev/null || echo "0")
    if [ "$TASK2A_PASS" -gt 0 ] 2>/dev/null; then
        echo "   ✅ REPORT.md contains PASS markers ($TASK2A_PASS occurrences)"
    else
        echo "   ❌ REPORT.md missing PASS markers"
        PASS=false
    fi

    if grep -q "REPORT_task2_flutter_screenshot.png" "$REPORT" 2>/dev/null; then
        echo "   ✅ Screenshot reference found in REPORT.md"
    else
        echo "   ❌ Screenshot reference missing from REPORT.md"
        PASS=false
    fi

    if [ -f "/root/se-toolkit-lab-8/REPORT_task2_flutter_screenshot.png" ]; then
        echo "   ✅ Screenshot file exists"
    else
        echo "   ❌ Screenshot file missing"
        PASS=false
    fi
else
    echo "   ❌ REPORT.md not found"
    PASS=false
fi

# Summary
echo ""
echo "============================================================"
if [ "$PASS" = true ]; then
    echo "RESULT: PASS"
    echo "Task 2 — Deployed Web Client: All checks passed"
else
    echo "RESULT: FAIL"
    echo "Task 2 — Some checks failed, see details above"
fi
echo "============================================================"
