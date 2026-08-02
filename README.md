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

## Manual connections

OpenCode, headless automation, and self-hosted hosts that differ from
`https://paperwork.bot` still use a manual `pwcap_` token from
**Setup -> API & MCP Access**. Keep it in an OS credential manager or process
environment, never in chat or a repository. Use a dedicated non-admin user for
unattended automation.

## What is included

| Skill | Responsibility |
| --- | --- |
| `paperwork` | Routes broad requests and mixed workflows |
| `paperwork-setup` | Installs, connects, diagnoses, rotates, and removes |
| `paperwork-account-guide` | Discovers account vocabulary and allowed values |
| `paperwork-triage` | Prioritizes personal, role, and held task queues |
| `paperwork-task-work` | Investigates and operates one task end to end |
| `paperwork-process-management` | Searches, creates, annotates, messages, and changes workflows |
| `paperwork-document-management` | Searches, inspects, reads, downloads, resolves, and reprocesses paperwork |
| `paperwork-intake` | Creates a workflow, assigns contacts, uploads files, and verifies processing |
| `paperwork-processing` | Follows an upload through processing, extraction, result inspection, and timeline review |
| `paperwork-contact-history` | Reviews one counterparty relationship |
| `paperwork-document-lookup` | Reconciles one or many document identifiers |
| `paperwork-custom-task-tools` | Discovers, invokes, and polls administrator-approved account-specific tools |

The current release intentionally covers all 33 operations exposed by the
fixed Paperwork MCP capability catalog plus opt-in direct custom-task tools.
It does not administer accounts, users, agents, custom-task definitions,
integrations, secrets, or arbitrary code.

See [`plugins/paperwork/README.md`](plugins/paperwork/README.md) for capability
profiles, safety boundaries, updates, and removal.

The stable install identifier remains `paperwork`, so existing
`paperwork@paperwork` installations update in place.
