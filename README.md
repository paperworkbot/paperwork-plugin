# PaperworkBot

PaperworkBot, from Kaytos, LLC, lets you operate
[Paperwork](https://paperwork.bot) from the Claude app, Claude Code, Codex, or
OpenCode. The remote connector gives Claude app users the Paperwork tools
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
environment, never in chat or a repository. Use a dedicated non-admin user for
unattended automation, and limit the token to the agents it serves.

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

The source package is version **0.14.1**. Its skills cover the fixed capability
catalog plus opt-in direct custom-task tools through live discovery.
It does not create agents or change their model, runtime, tool, integration,
secret, or arbitrary-code configuration.

See [`plugins/paperwork/README.md`](plugins/paperwork/README.md) for capability
profiles, safety boundaries, updates, and removal.

The stable install identifier remains `paperwork`, so existing
`paperwork@paperwork` installations update in place.
