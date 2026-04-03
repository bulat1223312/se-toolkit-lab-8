#!/bin/bash
# Task 4 Verification — Diagnose Failure and Make Agent Proactive
REPORT="/root/se-toolkit-lab-8/REPORT.md"
PASS=true

echo "=== Task 4 Verification ==="

# Check REPORT.md sections exist
for section in "Task 4A" "Task 4B" "Task 4C"; do
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

# Check 4A has investigation content (log evidence + trace evidence mentioned)
if grep -qi "log evidence" "$REPORT" && grep -qi "trace evidence" "$REPORT"; then
    echo "✅ 4A contains log and trace evidence"
else
    echo "⚠️ 4A missing investigation details"
fi

# Check 4B has cron/health check content
if grep -qi "cron\|health check\|scheduled" "$REPORT"; then
    echo "✅ 4B contains cron/health check evidence"
else
    echo "⚠️ 4B missing cron evidence"
fi

# Check 4C has bug fix content
if grep -qi "SQLAlchemyError\|500\|root cause" "$REPORT"; then
    echo "✅ 4C contains bug fix evidence"
else
    echo "⚠️ 4C missing bug fix evidence"
fi

# Check screenshot files
for img in task4b_cron_health_report.png task4c_healthy_followup.png; do
    if [ -f "/root/se-toolkit-lab-8/report-images/$img" ]; then
        echo "✅ Screenshot: $img"
    else
        echo "⚠️ Missing screenshot: $img"
    fi
done

# Check observability skill exists
if [ -f "/root/se-toolkit-lab-8/nanobot/workspace/skills/observability/SKILL.md" ]; then
    echo "✅ Observability skill exists"
    if grep -qi "what went wrong" "/root/se-toolkit-lab-8/nanobot/workspace/skills/observability/SKILL.md"; then
        echo "✅ SKILL.md includes 'What went wrong?' investigation flow"
    fi
else
    echo "❌ Observability skill missing"
    PASS=false
fi

# Check backend fix
if grep -qi "SQLAlchemyError" "/root/se-toolkit-lab-8/backend/app/routers/items.py"; then
    echo "✅ Backend fix in place (SQLAlchemyError handling)"
else
    echo "⚠️ Backend fix not detected in items.py"
fi

echo ""
if [ "$PASS" = true ]; then
    echo "PASS"
else
    echo "FAIL — some checks did not pass"
fi
