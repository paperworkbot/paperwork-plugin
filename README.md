# PaperworkBot

PaperworkBot, from Kaytos, LLC, lets you operate
[Paperwork](https://paperwork.bot) from Claude Code, Codex, or OpenCode. The
plugin gives a local agent safe procedures for account
discovery, queue triage, tasks, workflows, contacts, document intake,
document investigation, and paperwork resolution over Paperwork's
permission-scoped MCP server.

Every call runs as the user bound to the API token, within both that user's
current Paperwork permissions and the token's capability ceiling.

## Install

### Claude Code

```text
/plugin marketplace add paperworkbot/paperwork-plugin
/plugin install paperwork@paperwork
```

Set `PAPERWORK_MCP_TOKEN` and, for a self-hosted deployment,
`PAPERWORK_MCP_URL`. Run `/reload-plugins` or start a new session.

### Codex

```sh
codex plugin marketplace add paperworkbot/paperwork-plugin
codex plugin add paperwork@paperwork
codex mcp add paperwork \
  --url "$PAPERWORK_MCP_URL" \
  --bearer-token-env-var PAPERWORK_MCP_TOKEN
```

Start a new Codex task after installation.

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

## Connect securely

Create a personal token under **Setup -> API Access** in Paperwork with the
`mcp` audience and only the capabilities needed for your work. Tokens are
shown once and begin with `pwcap_`.

Prefer an OS credential manager or a silent prompt that populates the client
process environment. For one temporary zsh session:

```sh
read -s "PAPERWORK_MCP_TOKEN?Paperwork token: "; echo
export PAPERWORK_MCP_TOKEN
export PAPERWORK_MCP_URL="https://your-paperwork-host.example/mcp"
```

Managed-cloud users can omit `PAPERWORK_MCP_URL`; the bundled Claude
connection defaults to `https://paperwork.bot/mcp`.

The token limits operations, not records. Use a dedicated non-admin Paperwork
user when possible: account-scoped capabilities can reach everything that
user is currently allowed to see.

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
| `paperwork-contact-history` | Reviews one counterparty relationship |
| `paperwork-document-lookup` | Reconciles one or many document identifiers |

The current release intentionally covers all 32 operations exposed by the
Paperwork MCP capability catalog. It does not administer accounts, users,
agents, custom tasks, integrations, secrets, or arbitrary code.

See [`plugins/paperwork/README.md`](plugins/paperwork/README.md) for capability
profiles, safety boundaries, updates, and removal.

The stable install identifier remains `paperwork`, so existing
`paperwork@paperwork` installations update in place.
