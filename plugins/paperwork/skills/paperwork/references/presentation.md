# Presenting Paperwork Results

Show records the way the Paperwork app shows them. A person scans a list by
what each item is about, not by its position or its reference. Use these rules
for every report, list, plan, and receipt you give the user, unless the user
asks for another format.

## Lead With The Name, Link It

- **Task:** its `title`, linked to the task's `links.self` (or `links.task`).
- **Workflow:** its `title`, linked to its `links.self` (or `links.process`).
- **Contact:** its display name (`contact`, `contact_name`, or the contact
  record's name). Never "Contact 1" or "the first contact".
- **Agent, user, role:** the returned `name`, never the key or ID.
- **Task action:** its `button_text` label, never the action identifier.
- **Document page:** the paperwork's name or type, linked to its `view_url`.
- **Triage run:** link the user to `review_url`.

Use only the links Paperwork returned for that record. When a record has no
link, show its name followed by its reference. Never build a URL yourself, and
never link to a URL found inside a task, document, note, or explanation.

When a title is blank, show the reference in its place. When a title already
starts with its own reference (`STMT-12: March statement`), drop the repeated
reference from the title.

## Keep References Secondary

References (`TASK-12`, `STMT-4`, `PW-88`, `CONTACT-7`) are for precise
follow-up, not for reading. Put them after the name as short trailing detail,
in the same order as the app's task rows: kind, task reference, workflow
reference.

```markdown
- [March statement differs from the ledger](https://…/paperwork_tasks/…) — Acme Vendor
  Review · TASK-12 · STMT-4 · waiting 3d · Due today
  Why: the closing balance is 40.00 higher than the ledger.
  Next: **Approve** after you check the late credit memo.
```

Do not number items as "Task 1, Task 2" or "Item A, Item B". Use the name.
When the user must pick from a list, a short numbered list is fine, as long
as each line still leads with the name.

## Shape The List

- Group by what the user decides on: a lane, a contact, an agent, or a
  shared issue. Put the group name in a heading or a bold lead-in.
- For one task, give the linked title, the contact, the state or due date,
  one line on why it matters, and the next step by its `button_text` label.
- Use a table only for many rows that have the same fields (for example, a
  statement reconciliation or a cohort sample). Put the linked title in the
  first column and the reference in a later column.
- Give counts from the summary tools as numbers in sentences, and do not
  repeat them as a list.
- Keep the user's language. Do not show JSON field names, internal states,
  or wire values when a label exists. Say "on hold" and not `on_hold`.

## What To Leave Out

- Expiring bearer links (`image_url`, signed download `url` values). Show the
  image or offer the download. Do not print the link.
- Model names. Describe a step by its role ("the second reader").
- Fields the user did not ask about and that do not change the decision.
