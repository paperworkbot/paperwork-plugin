---
name: paperwork-triage
description: Triage the user's Paperwork queue over the Paperwork MCP connection. Use when the user asks "what needs my attention", "triage my paperwork", "what should I work on", "anything high priority?", "what's overdue", "check my queue", or wants a morning check-in on their tasks. Read-only - this skill surveys and prioritizes; it never completes, claims, or modifies tasks.
---

# Paperwork Triage

Survey the user's Paperwork task queue and tell them what matters most, so they
act on the top items instead of reading through everything.

Requires the Paperwork MCP server (tools named like `tasks_list`). If those
tools are unavailable, say the Paperwork connection is not set up and point the
user at the server's install instructions instead of improvising.

## Procedure

1. **My work**: call `tasks_list` with `{}`. This returns actionable tasks
   assigned to the user or their roles, ordered oldest due date first — already
   the right triage order. Note `total_count` and `has_more`.
2. **Unclaimed shared work**: call `tasks_list` with `{"queue": "role_queue"}`.
   These sit in a role queue with no owner — work nobody has picked up.
3. **Parked work**: call `tasks_list` with `{"state": "on_hold"}`. Old holds are
   often forgotten, not still blocked.
4. If `total_count` exceeds the page, fetch at most two more pages (`offset`).
   Never enumerate a huge queue; summarize the counts and triage what you have.

## Priority rubric

Bucket what came back, in this order:

1. **Overdue** — `due_at` in the past. Oldest first.
2. **Questions blocking a workflow** — tasks whose `task_type` is an ask-user
   question. The workflow's agent is stopped until someone answers; these are
   usually quick wins.
3. **Due within 48 hours.**
4. **Unclaimed role-queue tasks older than 2 days** — aging shared work.
5. **Stale holds** — on hold with no movement for a week or more.
6. Everything else, oldest first.

Use `description_preview`, `contact`, and `process` from each row to say *why*
an item matters (which contact, which workflow) — not just that it exists.

## Output

Lead with one headline sentence: total actionable items, how many overdue, how
many unclaimed. Then a short prioritized list — at most ten rows — each with the
task reference, title, contact when present, due date, and a one-line
reason it made the list. Close by recommending the top 2–3 and asking which to
work on.

Do not dump raw JSON or list every task. Selectivity is the value.

## Rules

- Triage is **read-only**. Do not call `tasks_claim`, `tasks_respond`,
  `tasks_hold`, or any other write during triage.
- When the user picks an item ("work on TASK-123", "handle the first one"),
  switch to the paperwork-task-work skill's procedure: investigate with
  `tasks_get` before acting, and confirm before any state change.
- If the queue is empty, say so plainly and check `role_queue` before
  concluding there is nothing to do.
