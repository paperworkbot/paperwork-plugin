# Public Release Boundary

This repository and all of its GitHub metadata are public distribution
surfaces. Treat files, history, commit and tag messages, releases, issues,
pull requests, Actions output, repository descriptions, and examples as
public.

Never publish:

- links or references to non-public repositories, issues, pull requests,
  branches, commits, or CI runs;
- workstation, checkout, or worktree paths;
- customer or tenant identifiers, document contents, credentials, tokens, or
  operational data;
- internal implementation plans, review notes, or deployment details.

Describe prerequisites generically, such as "a compatible Paperwork
deployment with MCP enabled."

Before publishing:

1. Run `ruby scripts/validate-plugin.rb`.
2. Scan the complete Git history and GitHub release, issue, pull-request, and
   repository metadata for non-public references.
3. Scan for credentials with a secret scanner.
4. Confirm the distribution tree exactly matches the reviewed source package.
5. Verify the release from its public URL after publication.
