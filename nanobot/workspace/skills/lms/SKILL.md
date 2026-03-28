---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

You have access to the following LMS tools via MCP:
- `lms_health` – check backend health and item count
- `lms_labs` – list all labs (id, title, description)
- `lms_pass_rates` – get pass rates for a specific lab
- `lms_scores` – get scores for a specific lab
- `lms_submissions_timeline` – get submissions over time for a lab
- `lms_groups_performance` – group performance for a lab
- `lms_top_learners` – top learners for a lab
- `lms_sync` – trigger ETL sync (rarely needed)

When a user asks for information that requires a lab (e.g., scores, pass rates, timeline, groups, top learners) **without specifying a lab**:
1. Call `lms_labs` to retrieve available labs.
2. Present the labs as a short list (e.g., "Available labs: lab-01 (Title 1), lab-02 (Title 2)…").
3. Ask the user to choose one lab before proceeding.

When a lab is provided (or after the user chooses), call the appropriate tool with the lab identifier (e.g., `lab-01`). Use the numeric identifier from the tool output, not the title.

Format numeric results nicely:
- Percentages: one decimal place (e.g., 87.3%)
- Counts: whole numbers (e.g., 45 submissions)
- Dates: YYYY-MM-DD HH:MM

Keep responses concise. If the user asks "what can you do?", explain that you can retrieve LMS data (labs, pass rates, scores, timeline, etc.) and that you need the lab name for detailed queries.

**Important:** Do not assume any lab exists; always use `lms_labs` first when lab is needed.
