---
name: paperwork-setup
description: Install, connect, verify, diagnose, rotate, or remove the Paperwork MCP connection for Claude Code, Codex, or OpenCode. Use when Paperwork tools are missing, authentication fails, one tool is forbidden, a host changes, a token must be rotated, or the user asks to set up PaperworkBot.
---

# Set Up PaperworkBot

Connect a local agent to the user's Paperwork host through sessionless
Streamable HTTP MCP.

## Normal User Setup

The managed-cloud plugin declares `https://paperwork.bot/mcp` as an OAuth MCP
server. After installation, use the client's authentication action:

1. Choose **Authenticate**, **Connect**, or **Log in** for Paperwork, depending
   on the client.
2. Sign in to Paperwork in the browser.
3. Review the client name and acting user, then choose **Allow access**.
4. Return to the client and start a new task if its tool catalog was already
   open.

Do not ask a managed-cloud user to create, copy, or export a token. The client
stores short-lived OAuth credentials in its own credential store and refreshes
them automatically.

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
- **Unauthorized:** choose the client's Paperwork authentication action. If
  already connected, disconnect and authorize again. For a manual token
  connection, the token may be missing, expired, revoked, or bound to a
  disabled user.
- **Forbidden on one tool:** connection is healthy, but the token ceiling or
  acting user's current Paperwork permission denies that capability.
- **Not found on one record:** do not treat this as connection failure; the
  record may be absent or outside the user's authorized view.
- **Rate limited:** honor `Retry-After`; do not rotate credentials or retry in a
  tight loop.

Use [the capability map](../paperwork/references/capabilities.yml) to identify
the missing grant and its owning workflow skill.

## Codex

Install the plugin from the marketplace. In **Settings -> MCP servers**, open
Paperwork and choose **Authenticate**. Codex opens Paperwork in the
browser and stores the resulting OAuth credentials in its credential store.
Start a new Codex task after connecting.

Paperwork advertises MCP read/write annotations so Codex can auto-approve
trusted reads while continuing to gate state-changing tools. Do not set a
blanket `approve` policy for every Paperwork tool.

## Claude Code

The installed plugin declares the OAuth server in `.mcp.json`. Use `/mcp`,
choose Paperwork, and authenticate in the browser. Run `/reload-plugins` or
start a new session if tools do not appear after authorization.

Do not add a second manual `paperwork` MCP server when the plugin server is
enabled; duplicate catalogs confuse tool selection.

## Claude App, Web, Mobile, And Cowork

Paperwork is a remote connector, so it is configured through the user's Claude
account rather than a desktop configuration file:

1. Open **Customize -> Connectors**.
2. Choose **Add custom connector**.
3. Enter `https://paperwork.bot/mcp`.
4. Choose **Connect**, sign in to Paperwork, and approve access.

Do not ask for an OAuth client ID or secret. Paperwork supports dynamic client
registration. Team and Enterprise plans require an Owner to add the custom
connector under **Organization settings -> Connectors** before members can
connect their own Paperwork accounts.

## Manual Tokens For Automation And Self-Hosting

Use a manual token only for headless automation, a client without MCP OAuth, or
a self-hosted Paperwork deployment whose URL differs from the managed-cloud
plugin default.

- `PAPERWORK_MCP_URL`: the deployment's absolute `/mcp` URL. Never guess a
  self-hosted host.
- `PAPERWORK_MCP_TOKEN`: a one-time `pwcap_...` value issued under
  **Setup -> API & MCP Access**, bound to one user and carrying the `mcp`
  audience.

The token is a bearer credential. Never ask the user to paste it into chat and
never echo it after entry. Prefer an OS credential manager or a silent prompt
that populates the client process environment. Do not put the token in command
arguments, repository files, `opencode.json`, task notes, or documents.

For Codex, remove or disable the managed-cloud plugin server before registering
a self-hosted server with `--bearer-token-env-var PAPERWORK_MCP_TOKEN`; duplicate
catalogs confuse tool selection.

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

## Disconnect, Rotate, Or Remove

For OAuth, use the client's **Disconnect** action and reconnect if needed.
Paperwork access also stops immediately when the acting user is deactivated.

For a manual token, issue a replacement with the same or narrower grants,
update the client credential without printing it, verify one read, and revoke
the prior token under **Setup -> API & MCP Access**.

## Production Guidance

OAuth runs as the person who approved access and remains bounded by that
person's current roles. For unattended manual-token automation, use a
dedicated non-admin Paperwork user whose roles bound record access.
