---
name: paperwork-contact-history
description: Review a contact's relationship in Paperwork over the Paperwork MCP connection - any counterparty the account works with. Use when the user asks "what's going on with <contact>", "history with Acme", "open items for them", "have we worked with them before", or wants the state of everything tied to one contact. Read-only.
---

# Contact History Review

Answer "what is our situation with this contact?" by walking the contact's
workflows, open items, and recent activity. A contact is any counterparty the
account works with.

Requires the Paperwork MCP server (tools named like `contacts_search`).

## Procedure

1. **Find the contact**: `contacts_search` with the name, account number, or
   external ID the user gave. If more than one plausible match comes back, list
   the candidates (name, account number, reference) and ask which one — never
   guess between similarly named contacts.
2. **Open work**: `processes_search` with
   `{"contact_reference": "...", "scope": "account", "state": "open"}`.
3. **Prior history**: the same call without the `state` filter shows completed
   and cancelled workflows for the full relationship picture.
4. **Drill into the active ones** — for up to three open workflows, `context_get`
   for outstanding tasks and paperwork, and `processes_history` (limit ~10) on
   the most active one when the user wants the story, not just the state.

## Output

A relationship summary, not a data dump:

- **Who**: display name, account number or external ID, contact reference.
- **Open now**: each open workflow with its reference, title, state, and what
  it is waiting on (outstanding tasks, on-hold reasons).
- **Recent history**: a line or two — how many workflows completed recently,
  anything cancelled or long-running.
- **Flags**: overdue tasks, workflows on hold, anything aging without
  movement.

Offer follow-ups: work one of the outstanding tasks (paperwork-task-work), or
check a specific document (paperwork-document-lookup).

## Rules

- Read-only. Do not modify tasks, workflows, or role assignments during a
  review.
- Do not enumerate every historical workflow for a high-volume contact —
  summarize counts and show the most recent handful.
- If the user's own permissions hide some workflows, the results already
  reflect that; present what came back without speculating about what didn't.
