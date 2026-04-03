---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

You have access to LMS MCP tools for querying live course data.

## Available Tools

- `lms_health` - Check if the LMS backend is healthy and report the item count
- `lms_labs` - List all labs available in the LMS
- `lms_learners` - List all learners registered in the LMS
- `lms_pass_rates` - Get pass rates (avg score and attempt count per task) for a lab (requires `lab` parameter)
- `lms_timeline` - Get submission timeline (date + submission count) for a lab (requires `lab` parameter)
- `lms_groups` - Get group performance (avg score + student count per group) for a lab (requires `lab` parameter)
- `lms_top_learners` - Get top learners by average score for a lab (requires `lab` parameter, optional `limit`)
- `lms_completion_rate` - Get completion rate (passed / total) for a lab (requires `lab` parameter)
- `lms_sync_pipeline` - Trigger the LMS sync pipeline

## Strategy Rules

1. **When user asks about scores, pass rates, completion, groups, timeline, or top learners without naming a lab:**
   - First call `lms_labs` to get available labs
   - If multiple labs exist, ask the user to choose one
   - Use each lab's `title` field as the user-facing label

2. **When presenting lab choices:**
   - Format as a numbered list with lab titles
   - Let the shared structured-ui skill handle presentation on supported channels

3. **When user asks "what can you do?":**
   - Explain that you can query live LMS data including labs, learners, pass rates, timelines, group performance, and completion statistics
   - Mention that you need a lab name for detailed queries

4. **Formatting:**
   - Format percentages with % symbol
   - Format counts as plain numbers
   - Keep responses concise and structured

5. **Error handling:**
   - If a tool fails, explain what went wrong and suggest alternatives
   - If the backend is unavailable, suggest checking system health
