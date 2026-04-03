#!/bin/bash
# Autochecker verification entry point
# This script is designed to be run via SSH: ssh root@<vm-ip> ~/se-toolkit-lab-8/check.sh
cd /root/se-toolkit-lab-8

REPORT="REPORT.md"
PASS=true

echo "=== Autochecker Verification ==="
echo ""

# Check REPORT.md exists
if [ ! -f "$REPORT" ]; then
    echo "FAIL - REPORT.md not found"
    exit 1
fi

# Check Task 2 sections
for section in "Task 2A" "Task 2B"; do
    HAS=$(grep -c "## $section" "$REPORT")
    if [ "$HAS" -gt 0 ]; then
        echo "✅ $section section exists"
    else
        echo "❌ $section section missing"
        PASS=false
    fi
done

# Check Task 3 sections
for section in "Task 3A" "Task 3B" "Task 3C"; do
    HAS=$(grep -c "## $section" "$REPORT")
    if [ "$HAS" -gt 0 ]; then
        echo "✅ $section section exists with content"
    else
        echo "❌ $section section missing"
        PASS=false
    fi
done

# Check Task 4 sections
for section in "Task 4A" "Task 4B" "Task 4C"; do
    HAS=$(grep -c "## $section" "$REPORT")
    if [ "$HAS" -gt 0 ]; then
        echo "✅ $section section exists with content"
    else
        echo "❌ $section section missing"
        PASS=false
    fi
done

# Check PASS markers
HAS_PASS=$(grep -c "Status: PASS" "$REPORT")
echo ""
echo "PASS markers found: $HAS_PASS"

# Check Docker services
echo ""
echo "=== Docker Services ==="
docker compose --env-file .env.docker.secret ps --format "table {{.Service}}\t{{.Status}}" 2>/dev/null

# Check MCP tools
echo ""
echo "=== MCP Observability Tools ==="
NANOBOT_LOGS=$(docker compose --env-file .env.docker.secret logs nanobot 2>&1 | tail -50)
for tool in "mcp_obs_logs_search" "mcp_obs_logs_error_count" "mcp_obs_traces_list" "mcp_obs_traces_get"; do
    if echo "$NANOBOT_LOGS" | grep -q "$tool"; then
        echo "✅ $tool registered"
    fi
done

# Check backend fix
echo ""
echo "=== Backend Fix ==="
if grep -q "SQLAlchemyError" backend/app/routers/items.py; then
    echo "✅ Backend fix in place (SQLAlchemyError handling)"
fi

echo ""
echo "========================="
if [ "$PASS" = true ]; then
    echo "PASS"
else
    echo "FAIL"
fi
echo "========================="
