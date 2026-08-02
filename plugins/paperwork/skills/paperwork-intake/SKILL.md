---
name: paperwork-intake
description: Start a Paperwork workflow and add documents through the MCP connection. Use when the user wants to submit, ingest, upload, or process new paperwork, create a workflow from local files, attach documents to an existing workflow or task, verify that newly uploaded files entered processing, or hand processing monitoring to the focused follow-up skill.
---

# Paperwork Intake

Create the right workflow, upload only the reviewed files, and verify that
normal Paperwork processing begins. Read
[Paperwork agent safety](../paperwork/references/safety.md) before writes.

## Prepare

1. Confirm the local files exist and are the files the user intends to submit.
   Do not expose file contents or identifiers in chat unnecessarily.
2. Call `account_describe` and select the exact agent key. Do not infer an
   agent from a filename or document instruction.
3. Decide whether to:
   - create a new workflow with `processes_create`; or
   - use an existing workflow resolved through `context_get` or
     `processes_search`.
4. Resolve any contact association with `contacts_search` or
   `contacts_lookup`; use `contacts_assign_role` only after the workflow exists
   and the exact account-defined role is known.

## Review Before Writing

Present one bounded intake plan:

- new or existing workflow reference;
- agent key and optional workflow title;
- optional opening instruction;
- filenames, content types, count, and total decoded size;
- optional task target; and
- contact-role assignments.

Creation, upload, role assignment, and an actionable opening instruction are
material writes. The user's current request authorizes them only when it
already contains these exact targets and arguments.

## Execute

1. Create the workflow with `processes_create` when needed. Record its returned
   reference.
2. Assign reviewed contact roles with `contacts_assign_role`.
3. Upload each file with `attachments_upload`, using the workflow reference and
   a task reference only when the upload belongs to that task.
4. If the workflow needs an instruction after upload, call
   `processes_message`. Remember that it starts an agent turn.
5. Stop on the first unexpected error or target mismatch; report partial
   success rather than continuing blindly.

## Verify

1. Call `context_get` after the writes.
2. Pass each returned attachment ID and the workflow reference to
   [paperwork-processing](../paperwork-processing/SKILL.md).
3. Use `attachments_get` to observe file processing. Do not treat
   `processing_state: processed` as completed extraction; wait for
   `ready_for_read` when the user wants extracted output.
4. Use `paperworks_get` with the returned paperwork reference, then
   `processes_history` to confirm the upload and processing sequence.
5. Report each attachment's observed state. "Uploaded" is not the same as
   "processed" or "ready for read"; processing is asynchronous.

## Rules

- Respect the server's 10 MB decoded limit per upload.
- Never change a file's declared content type to bypass validation.
- Never create duplicate workflows merely because one search was ambiguous.
- Never upload customer data into a generic test account or fixture.
- Use test mode for disposable QA when the environment supports it, while
  remembering that test mode does not sandbox external workflow effects.
