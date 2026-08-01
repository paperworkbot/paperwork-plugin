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

1. Run `ruby scripts/validate-plugin_test.rb` and
   `ruby scripts/validate-plugin.rb`.
2. Scan the complete Git history with Gitleaks.
3. Inspect GitHub activity for force-pushed or otherwise orphaned commits. A
   clean replacement repository is required when an orphaned object crosses
   the public boundary; rewriting branch history alone is not sufficient.
4. Review releases, issues, pull requests, Actions output, and repository
   metadata for non-public references.
5. Confirm the distribution tree exactly matches the reviewed source package.
6. Verify the release from its public URL after publication.
