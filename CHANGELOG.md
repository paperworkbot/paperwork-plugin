# Changelog

All notable changes to the PaperworkBot plugin and portable Agent Skills are
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.20.0]

### Added

- Standalone `CHANGELOG.md` validated against the package manifests on every
  change; release history no longer lives inline in `README.md`.
- End-to-end task-type and task-kind resolution guidance across the skills:
  structured task-kind reviews (`collection_review` on `tasks_get` and
  `collection_revision` on `tasks_respond`, including part-mapping `remember`
  translations and note-only answers on unbound rows), contact-match candidate
  details and `trust_sender` on `tasks_resolve_contact`, guided-review plain
  questions and `decision: "rebuild"` on `tasks_review_decision`, filing tasks
  under task kinds with `tasks_classify`, approving or dismissing drafted
  answers with `tasks_review_suggestion`, and creating or reviewing delegated
  handoffs with `tasks_delegation`.
- Direct `task_kind`, `task_reason`, `list_id`, and `due: "none"` filters on
  task queue, summary, tile, report, and triage tools, plus `task_kinds`
  breakdowns on `tasks_summary`.
- Bulk contact resolution (`resolve_contact`) and bulk task classification
  (`classify`) in `tasks_bulk`.
- Contact mapping and counterparty guidance: `contact_match_groups` on
  `decisions_list`, instant `mode: "map"` and `mode: "instruct"` runs on
  `triage_runs_create`, `contact_reference` and `user_email` support in
  `triage_runs_prepare_apply` `group_actions`, richer `contacts_search`
  (aliases, company names, emails, status, classification, cursor paging),
  inactive-contact discovery in `contacts_lookup`, operational edits
  (`custom_instructions`, `contact_status`, `contact_classification`) on
  externally managed contacts, and `contacts_review_note_revision`.
- Document maintenance guidance for deleting spurious extracted fields
  (`delete: true` on `paperworks_update_field`) and dismissing false-positive
  duplicate flags (`paperworks_dismiss_duplicates`), plus `wake_platform_hold`
  on `processes_retry_agent` for account administrators.
- Identifier rules (`identifier_rules_list`, `identifier_rules_get`,
  `identifier_rules_preview`, `identifier_rules_create`,
  `identifier_rules_update`, `identifier_rules_delete`) and `identifier_rule`
  filtering on `paperworks_find_by_identifier`.
- Workflow snoozing (`processes_snooze`) to hold a workflow until a chosen time
  with a wake instruction.
- Idempotent triage review marking (`tasks_mark_reviewed`) and compact task
  lists (`fields: "compact"` on `tasks_list`).
- Optional board list descriptions (`description`) on `boards_create_list`,
  `boards_update_list`, and `boards_list`.

### Fixed

- `paperwork-setup` now states accurately that refreshing an OAuth token keeps
  existing grants and drops retired ones, while newly added server capabilities
  require reconnecting so the user approves the expanded tool surface.
- Capability tier tables in `plugins/paperwork/README.md` and `safety.md` now
  cover every advertised capability in the catalog.

## [0.19.1] - 2026-11-10

Includes the changes from `0.18.1` and `0.19.0`, which were not published as
separate releases.

### Added

- Task-work recipe for working a cohort end to end: find tasks by kind, export
  their documents' fields for a CSV, download their files, and answer or close
  them in one confirmed batch.

## [0.19.0]

### Added

- Decision-first queue triage: `decisions_list` groups open tasks in the user's
  queue by agent, kind, and reason across contacts, with counts and the usual
  earlier answer, and `triage_runs_create` accepts `across_contacts` to review
  one decision's tasks together. The triage and check-in skills lead with
  decisions.

## [0.18.1]

### Changed

- Cleaned up `README.md` and `paperwork-account-review` wording; behavior is
  unchanged.

## [0.18.0] - 2026-11-10

Includes the changes from `0.16.2`, `0.16.3`, and `0.17.0`, which were not
published as separate releases.

### Added

- `paperwork-account-review` skill to review how an account's agents worked
  from exact reports and submit proposals (`reviews_submit`) that wait for
  people.
- Counterparty knowledge management: `learnings_create` accepts document types,
  a playbook step, and evidence in one call; `learnings_get` returns every
  field with the workflows it reached; `translations_list`,
  `translations_create`, and `translations_review` manage how a counterparty
  writes a value and what we call it; `contacts_set_attribute` and
  `contacts_review_attribute` manage typed contact business facts; and
  `contacts_update` supports partial edits via `instructions_edit`.
- Account data reports (`reports_create`, `reports_get`, `reports_cancel`).

## [0.17.0]

### Added

- Drafted answers: `tasks_suggest` saves a resolution for a person to approve
  without acting, and `tasks_suggestions` lists drafts waiting in a queue. The
  triage skill explains when to draft instead of asking a person to type an
  answer.

## [0.16.3]

### Changed

- Shared presentation rules (`presentation.md`): skills lead with a task's or
  workflow's linked title, name contacts and actions, and keep references as
  trailing detail instead of numbering results.

## [0.16.2]

### Added

- Guidance in `paperwork-agent-operations` for `tasks_report` with
  `health: true` to inspect each task kind's last 30 days and open queue.

## [0.16.1] - 2026-11-10

### Added

- Grouped-review guidance in `paperwork-triage`: how look-alike tasks are
  grouped, Map to contact, and `group_actions` choices on
  `triage_runs_prepare_apply`.
- Read capabilities for task, workflow, and contact reports, account settings,
  and instruction search and history, plus `task_kinds_classify` and
  `task_kinds_dismiss_suggestion`.

### Changed

- Replaced `learnings_promote_to_sop` with `learnings_review_sop_change`,
  showing every suggested edit as a diff before confirmation.

## [0.16.0] - 2026-10-12

### Added

- Filtering workflows and tasks on extracted fields through `fields_list` and
  validated filter plans or plain-language questions, plus grouped summary
  reports.

## [0.15.1] - 2026-10-10

### Changed

- Updated plugin introductions and client descriptions to lead directly with
  supported clients and workflows.

## [0.15.0] - 2026-10-10

### Added

- Task review tiles (`tasks_present`), document previews without an associated
  task (`paperworks_present`), exact intake summaries (`paperworks_summary`),
  verification signals, and bounded precedent summaries.

## [0.14.2] - 2026-10-09

### Changed

- Added continuation guidance for bulk updates that stop early with
  `deferred_references` and a fresh `idempotency_key`.

## [0.14.1] - 2026-10-09

### Added

- Expanded to 16 skills, 90 fixed capabilities, and 18 behavioral evaluation
  cases, including board management, bulk workflow and task operations, guided
  reviews, and user-authority safety rules.

## [0.11.0] - 2026-09-16

### Added

- Permission-scoped account data discovery, scan, and JSONL export
  (`data_describe`, `data_scan`, `data_export`), local statement reconciliation,
  account-run recovery guidance, and agent/SOP operations.

## [0.9.1] - 2026-09-01

### Fixed

- Kept the Codex starter-prompt list within the three-prompt client limit and
  enforced the bound in `scripts/validate-plugin.rb`.

## [0.9.0] - 2026-09-01

### Added

- Dedicated read-only `paperwork-check-in` skill separated from hosted triage
  runs.

## [0.5.1] - 2026-08-02

### Fixed

- Restored PaperworkBot logo and brand metadata in the Codex manifest.

## [0.5.0] - 2026-08-02

### Added

- Browser-based MCP OAuth 2.1 connection support with no manual bearer-token
  configuration required for Claude Code or Codex.

## [0.2.4] - 2026-08-02

### Added

- Bundled Paperwork SVG icon and brand color metadata for Codex plugin
  surfaces.

## [0.2.3] - 2026-08-01

### Added

- Public-release boundary validation across files, Git history, release notes,
  and CI secret scanning.

## [0.2.2] - 2026-08-01

### Changed

- Standardized PaperworkBot product naming and Kaytos, LLC publisher metadata
  while keeping the `paperwork` install identifier stable.

## [0.2.1] - 2026-08-01

### Added

- Separate MCP configuration examples and validation for both OpenCode v1 and
  OpenCode v2.

## [0.2.0] - 2026-08-01

### Added

- Ten portable Agent Skills covering queue triage, task work, workflow
  lifecycle management, document intake, processing follow-through, account
  vocabulary, contact history, and document lookup, plus the OpenCode installer
  and behavioral safety evaluations.
