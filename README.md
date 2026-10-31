# PaperworkBot

Operate [Paperwork](https://paperwork.bot) from the Claude app, Claude Code,
Codex, or OpenCode. The remote connector gives Claude app users the Paperwork tools
directly; the plugin adds safe procedures for account discovery, queue triage,
tasks, workflows, contacts, document intake, processing follow-through,
document investigation, and paperwork resolution.

Managed-cloud users sign in through Paperwork in the browser. Every call runs
as that signed-in user and stays inside their current Paperwork permissions.

## Install

### Claude app, web, or mobile

Open **Customize -> Connectors**, choose **Add custom connector**, and enter:

```text
https://paperwork.bot/mcp
```

Choose **Connect**, sign in to Paperwork, and approve access. The connection
syncs through the user's Claude account, so it is available in Claude web,
Desktop, mobile, Cowork, and Claude Code. Team and Enterprise plans require an
Owner to add the custom connector to the organization first.

### Claude Code

```text
/plugin marketplace add paperworkbot/paperwork-plugin
/plugin install paperwork@paperwork
```

Open `/mcp`, choose Paperwork, and authenticate in the browser. Run
`/reload-plugins` or start a new session after connecting.

### Codex

```sh
codex plugin marketplace add paperworkbot/paperwork-plugin
codex plugin add paperwork@paperwork
```

In **Settings -> MCP servers**, open Paperwork and choose **Authenticate**.
Sign in to Paperwork in the browser, approve access, and start a
new Codex task.

### OpenCode

Clone this repository, install the portable Agent Skills, and merge the MCP
example into your OpenCode configuration:

```sh
./scripts/install-opencode.sh
```

Use [`opencode.example.jsonc`](opencode.example.jsonc) for stable OpenCode v1,
or [`opencode-v2.example.jsonc`](opencode-v2.example.jsonc) for OpenCode v2,
whose server entries live under `mcp.servers`. OpenCode reads the token from
the process environment; never paste it into the configuration file.

## Self-hosted Paperwork

Claude Code reads the server URL from `PAPERWORK_MCP_URL` and falls back to
`https://paperwork.bot/mcp`. Set it to your deployment's `/mcp` URL in the
environment that starts Claude Code, then authenticate in the browser as
usual. Codex users register a self-hosted server with `codex mcp add`; see the
`paperwork-setup` skill.

## Manual connections

OpenCode and headless automation use a manual `pwcap_` token from
**Setup -> API & MCP Access**. Keep it in an OS credential manager or process
environment, never in chat or a repository. A token acts as the user who
creates it, so for unattended automation sign in as a dedicated non-admin user,
create the token there, and limit it to the agents it serves.

## What is included

| Skill | Responsibility |
| --- | --- |
| `paperwork` | Routes broad requests and mixed workflows |
| `paperwork-setup` | Installs, connects, diagnoses, rotates, and removes |
| `paperwork-account-guide` | Discovers account vocabulary and allowed values |
| `paperwork-account-data` | Queries account datasets and assembles verified private JSONL exports for local analysis |
| `paperwork-check-in` | Produces read-only daily status, priorities, blockers, and next steps |
| `paperwork-triage` | Queues hosted triage runs and applies their reviewed recommendation plans |
| `paperwork-task-work` | Investigates and operates one task end to end, or one confirmed action across many tasks |
| `paperwork-process-management` | Searches, creates, annotates, messages, assigns, and changes workflows, including bulk changes and board moves |
| `paperwork-document-management` | Searches, inspects, reads, downloads, resolves, and reprocesses paperwork |
| `paperwork-intake` | Creates a workflow, assigns contacts, uploads files, and verifies processing |
| `paperwork-processing` | Follows an upload through processing, extraction, result inspection, and timeline review |
| `paperwork-contact-history` | Reviews one counterparty relationship |
| `paperwork-document-lookup` | Reconciles one or many document identifiers |
| `paperwork-statement-reconciliation` | Reconciles a local statement file against Paperwork and the system of record without uploading it |
| `paperwork-custom-task-tools` | Discovers, invokes, and polls administrator-approved account-specific tools |
| `paperwork-agent-operations` | Edits contacts, workflow details, agent instructions, SOPs, assignments, and reviewed learnings with version checks |
| `paperwork-account-review` | Reviews how an account's agents worked from exact reports and submits proposals that wait for people (`reviews_submit`) |

The source package is version **0.18.0**. Its skills cover the fixed capability
catalog plus opt-in direct custom-task tools through live discovery.
It does not create agents or change their model, runtime, tool, integration,
secret, or arbitrary-code configuration.

Version 0.18.0 manages counterparty knowledge. `learnings_create` takes
document types, a playbook step and evidence in one call, and `learnings_get`
returns every field with the workflows it reached. `translations_list`,
`translations_create` and `translations_review` manage how a counterparty
writes a value and what we call it, and `contacts_update` can append to or
replace part of a contact's instructions with `instructions_edit`.
`contacts_set_attribute` and `contacts_review_attribute` set, confirm and reject
a contact's typed business facts (payment terms, currency, PO rule and the
like), and `contacts_get` lists them. An older deployment does not serve the
translation or business-fact tools.

Version 0.17.0 adds drafted answers. `tasks_suggest` saves a resolution for a
person to approve (the button, the form values, the note, the reasons and the
evidence) without acting, and `tasks_suggestions` lists the drafts waiting in a
queue. The triage skill explains when to draft instead of asking a person to
type an answer. It needs a deployment with ADR-014 (Paperwork bot drafts); an
older deployment does not serve the two tools.

Version 0.16.3 updates how the skills present records: a new shared reference
(`presentation.md`) tells the agent to lead with a task's or workflow's title,
name contacts and actions, and put the reference after the name instead of
numbering results. The wording changes only; no tool payload changes and no new
capability is needed. Update an existing plugin install to get it.

Version 0.16.2 updates the agent-operations skill: `tasks.report` with
`health: true` shows each task kind's last 30 days and open queue. It needs a
deployment at v0.29.0 or later. No new capability is needed; update an existing
plugin install.

Version 0.16.1 updates the triage skill for grouped reviews: how look-alike
tasks are grouped, Map to contact, and the `group_actions` choices that
`triage_runs_prepare_apply` accepts. Without a choice, a task that still asks
who its contact is refuses the default button. It needs a deployment at
v0.27.0 or later (the document-matched supplier rule it describes needs
v0.28.0). No new capability is needed; update an existing plugin
install.

Version 0.16.0 adds guidance for filtering workflows and tasks on the fields
that agents extract. The skills call `fields.list` to find those fields, then
apply a filter plan or a plain-language question. Summary reports group and
summarize the matching records. Use a compatible Paperwork deployment with the
`fields.list` MCP capability enabled, update an existing plugin install, and
reauthorize the MCP connection if `fields.list` is missing. Existing permission
and write confirmation rules still apply.

Version 0.15.0 adds guidance for task review tiles, document previews without
an associated task, and exact intake summaries. Review tiles can include
verification signals and bounded precedent examples when the connection has
the required grants. Use a compatible Paperwork deployment with these MCP
capabilities enabled, update an existing plugin install, and reauthorize the
MCP connection if the new tools are missing. Existing permission and write
confirmation rules still apply.

See [`plugins/paperwork/README.md`](plugins/paperwork/README.md) for capability
profiles, safety boundaries, updates, and removal.

The stable install identifier remains `paperwork`, so existing
`paperwork@paperwork` installations update in place.
