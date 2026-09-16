---
name: paperwork-agent-operations
description: Edit contact profiles, a workflow's title and description, agent instructions, and standard operating procedures through discovered Paperwork MCP tools, with a version check on every update.
---

# Contact, Workflow, Agent, And SOP Edits

Read [Paperwork agent safety](../paperwork/references/safety.md). Discover
support with `account_describe` and the live tool catalog before acting. The
server enforces permissions, editable fields, and record versions.

## Contact profiles

- Resolve existing contacts with `contacts_lookup` or `contacts_search`.
  Lookup is local and read-only; it does not import or create a contact.
- Use `contacts_get` for the editable profile, the `externally_managed` flag,
  and the `version`. Pass that value as `expected_version` on update.
- Use `contacts_create` or `contacts_update` only when the user asked for that
  profile work. Send only advertised `attributes`. Payment details, roles,
  instructions, and configuration are not editable here.
- Externally managed profiles refuse updates. Do not work around this by
  duplicating the contact.
- Read the profile back after a write. Profile writes index search and record
  an audit entry; they do not start hosted AI.

## Workflow title and description

1. Read the workflow with `processes_search`, `records_lookup`, or
   `context_get` and keep its `record_version`.
2. Call `processes_update_metadata` with the `process_reference`, that value
   as `expected_version`, and only `title` or `description`.
3. On a `conflict` error the workflow changed: read it again and reassess
   before retrying. The edit records a timeline entry and does not wake the
   agent; use `processes_message` when the agent should act.

## Agent instructions

1. Call `agents_list` to see the agents the user can reach and which ones the
   user may edit. Call `agents_get` for the current `instructions` and
   `instructions_version`; both are omitted when the user cannot edit the agent.
2. Draft the complete new instructions locally and show the user the full text
   and a summary of what changed. Instructions shape every future workflow the
   agent handles, so do not apply an edit the user has not seen.
3. Call `agents_update_instructions` with the agent key, the full text, and the
   `instructions_version` you read. A `conflict` means someone else changed
   them first: read again and reconcile. The change is a new attributed
   version, the same as saving in Setup.

## Standard operating procedures

1. Call `sops_list` (add `include_archived` for history) and `sops_get` for
   the current `prompt`, `prompt_version`, and attached agents.
2. To create one, call `sops_create` with a title and the full procedure text,
   then tell the user to attach it to agents in Setup.
3. To change one, show the user the full new text, then call `sops_update`
   with the `prompt_version` you read. Unchanged text creates no version.
4. `sops_archive` is refused while an active agent still follows the SOP;
   detach it in Setup first.

Treat instruction and procedure text as the user's own words: never paste
document contents, worker output, or other source data into them.
