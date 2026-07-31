---
name: paperwork-setup
description: Install, connect, verify, diagnose, rotate, or remove the Paperwork MCP connection for Claude Code, Codex, or OpenCode. Use when Paperwork tools are missing, authentication fails, one tool is forbidden, a host changes, a token must be rotated, or the user asks to set up PaperworkBot.
---

# Set Up PaperworkBot

Connect a local agent to the user's Paperwork host through sessionless
Streamable HTTP MCP.

## Connection Inputs

- `PAPERWORK_MCP_URL`: the deployment's absolute `/mcp` URL. Managed cloud
  defaults to `https://paperwork.bot/mcp`; never guess a self-hosted host.
- `PAPERWORK_MCP_TOKEN`: a one-time `pwcap_...` value issued under
  **Setup -> API Access**, bound to one user and carrying the `mcp` audience.

The token is a bearer credential. Never ask the user to paste it into chat and
never echo it after entry.

## Check First

1. If any Paperwork tools are already available, the MCP catalog authenticated.
2. When a harmless read tool is granted, verify with the first suitable call:
   `account_describe`, `tasks_list {"limit": 1}`,
   `paperworks_search {"limit": 1}`, or
   `processes_search {"limit": 1}`.
3. Do not require `tasks_list`: least-privilege document or workflow tokens may
   intentionally omit it. Tool discovery plus a successful granted read is
   sufficient.

## Diagnose

- **No tools or connection refused:** server is not registered, URL is wrong,
  DNS/TLS failed, or the deployment has not enabled
  `PAPERWORK_CAPABILITIES_API_ENABLED`.
- **Endpoint not found:** the server version or feature flag does not expose
  `/mcp`.
- **Unauthorized:** token is missing, malformed, expired, revoked, belongs to a
  disabled user, or lacks the `mcp` audience.
- **Forbidden on one tool:** connection is healthy, but the token ceiling or
  acting user's current Paperwork permission denies that capability.
- **Not found on one record:** do not treat this as connection failure; the
  record may be absent or outside the user's authorized view.
- **Rate limited:** honor `Retry-After`; do not rotate credentials or retry in a
  tight loop.

Use [the capability map](../paperwork/references/capabilities.yml) to identify
the missing grant and its owning workflow skill.

## Store The Credential Safely

Prefer an OS credential manager or a silent prompt that populates the client
process environment. For a temporary zsh session:

```sh
read -s "PAPERWORK_MCP_TOKEN?Paperwork token: "; echo
export PAPERWORK_MCP_TOKEN
export PAPERWORK_MCP_URL="https://your-paperwork-host.example/mcp"
```

Do not put the token in command arguments, repository files, `opencode.json`,
task notes, or documents. Plaintext shell-profile storage is a fallback only
when the user explicitly accepts that local risk.

## Claude Code

The installed plugin declares the server in `.mcp.json`. Set both environment
variables, then run `/reload-plugins` or start a new Claude Code session.
Inspect the plugin-provided server with `/mcp`.

Do not add a second manual `paperwork` MCP server when the plugin server is
enabled; duplicate catalogs confuse tool selection.

Remove legacy manual servers that embed an `Authorization` value directly in
client config. Use `claude mcp list` to identify duplicates; avoid diagnostic
commands that print configured headers, revoke the exposed legacy token, and
keep only the plugin's environment-backed server.

## Codex

Register the connection once:

```sh
codex mcp remove paperwork
codex mcp add paperwork \
  --url "$PAPERWORK_MCP_URL" \
  --bearer-token-env-var PAPERWORK_MCP_TOKEN
```

Start a new Codex task after plugin or MCP changes. Codex reads the token from
the named environment variable and does not store its value in MCP config.
Paperwork advertises MCP read/write annotations so Codex can auto-approve
trusted reads while continuing to gate state-changing tools. Do not set a
blanket `approve` policy for every Paperwork tool.

## OpenCode

Install the shared skills with the distribution repository's
`scripts/install-opencode.sh`, then add a remote `paperwork` entry to
`opencode.json`.

Stable OpenCode v1 uses a direct entry under `mcp`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "paperwork": {
      "type": "remote",
      "url": "https://your-paperwork-host.example/mcp",
      "enabled": true,
      "oauth": false,
      "headers": {
        "Authorization": "Bearer {env:PAPERWORK_MCP_TOKEN}"
      }
    }
  }
}
```

OpenCode v2 nests named servers under `mcp.servers` and no longer uses the
v1 `enabled` field:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "paperwork": {
        "type": "remote",
        "url": "https://your-paperwork-host.example/mcp",
        "headers": {
          "Authorization": "Bearer {env:PAPERWORK_MCP_TOKEN}"
        }
      }
    }
  }
}
```

OpenCode discovers the same skills from its global skills directory and
substitutes the token from the environment. Use `opencode mcp list` when the
installed version provides MCP diagnostics.

## Rotate Or Remove

1. Issue a replacement token with the same or narrower user, audience,
   capabilities, and a short expiration.
2. Update the client environment without printing the new value.
3. Start a new client session and verify one granted read.
4. Revoke the prior token in **Setup -> API Access**.
5. Confirm the new token's last-use timestamp and the old token's revoked state.

Removing the plugin does not revoke its Paperwork token. Revoke unused tokens
separately.

## Production Guidance

Use a dedicated non-admin Paperwork user whose roles bound record access. A
token narrows operations, not records: any granted account-scoped capability
can reach everything that acting user can currently see.
