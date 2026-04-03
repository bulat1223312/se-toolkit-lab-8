#!/bin/bash
# Task 3 Verification — Observability
REPORT="/root/se-toolkit-lab-8/REPORT.md"
PASS=true

# Check REPORT.md sections exist with content
for section in "Task 3A" "Task 3B" "Task 3C"; do
    HAS=$(grep -c "## $section" "$REPORT" 2>/dev/null)
    if [ "$HAS" -gt 0 ]; then
        echo "✅ $section section exists"
    else
        echo "❌ $section section missing"
        PASS=false
    fi
done

# Check PASS markers
HAS_PASS=$(grep -ci "PASS" "$REPORT" 2>/dev/null)
echo "PASS markers in REPORT.md: $HAS_PASS"

# Check screenshot files
for img in victorialogs_query.png victoriatraces_healthy.png victoriatraces_error.png; do
    if [ -f "/root/se-toolkit-lab-8/report-images/$img" ]; then
        echo "✅ Screenshot: $img"
    else
        echo "⚠️ Missing screenshot: $img"
    fi
done

# Check MCP tools registered
echo ""
echo "Checking MCP observability tools..."
NANOBOT_LOGS=$(docker compose -f /root/se-toolkit-lab-8/docker-compose.yml --env-file /root/se-toolkit-lab-8/.env.docker.secret logs nanobot 2>&1 | tail -50)
for tool in "mcp_obs_logs_search" "mcp_obs_logs_error_count" "mcp_obs_traces_list" "mcp_obs_traces_get"; do
    if echo "$NANOBOT_LOGS" | grep -q "$tool"; then
        echo "✅ MCP tool registered: $tool"
    else
        echo "⚠️ MCP tool not found in recent logs: $tool"
    fi
done

# Check observability skill
if [ -f "/root/se-toolkit-lab-8/nanobot/workspace/skills/observability/SKILL.md" ]; then
    echo "✅ Observability skill exists"
else
    echo "❌ Observability skill missing"
    PASS=false
fi

# Check mcp-obs module
if [ -f "/root/se-toolkit-lab-8/mcp/mcp_obs/src/mcp_obs/server.py" ]; then
    echo "✅ mcp-obs MCP server exists"
else
    echo "❌ mcp-obs MCP server missing"
    PASS=false
fi

echo ""
if [ "$PASS" = true ]; then
    echo "PASS"
else
    echo "FAIL — some checks did not pass"
fi
