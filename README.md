# Paperwork Plugin

Connect your coding agent — Claude Code or Codex — to [Paperwork](https://paperwork.bot):
triage your queue, investigate workflows and documents, review contact
history, and resolve tasks, always as you and within your Paperwork
permissions.

## Install

**Claude Code**

```text
/plugin marketplace add paperworkbot/paperwork-plugin
/plugin install paperwork@paperwork
```

**Codex**

```sh
codex plugin marketplace add paperworkbot/paperwork-plugin
codex plugin add paperwork@paperwork
```

Then set your connection (a `pwcap_...` token from **Setup -> API Access** in
Paperwork; the URL only if self-hosted):

```sh
export PAPERWORK_MCP_TOKEN="pwcap_..."
export PAPERWORK_MCP_URL="https://<your-host>/mcp"   # omit on managed cloud
```

Restart your agent and say **"set up paperwork"** to verify the connection.

## What's inside

| Skill | What it does |
| --- | --- |
| `paperwork-triage` | "What needs my attention?" — surveys and prioritizes your queue. Read-only. |
| `paperwork-task-work` | Investigates one task, proposes an action with evidence, acts only after you confirm. |
| `paperwork-contact-history` | The full picture of one contact: open work, history, flags. Read-only. |
| `paperwork-document-lookup` | "Have we seen this document, and where does it stand?" Read-only. |
| `paperwork-setup` | Connects or repairs the MCP link. |

See [plugins/paperwork/README.md](plugins/paperwork/README.md) for the token
capabilities each skill needs, so an administrator can grant exactly as much
as you use.

The plugin contains no credentials. Your API token is bound to your Paperwork
user, can be revoked at any time, and its capability ceiling is the hard limit
on what your agent can do — regardless of what it is asked.
