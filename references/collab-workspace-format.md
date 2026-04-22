# Collab Workspace Format

Use `collab-workspace.md` as the shared source of truth for agent identity, active ownership, and handoffs.

## Canonical Layout

```markdown
# Collaboration Workspace

## Agent Roster

| Agent | Role | Status | Scope |
| --- | --- | --- | --- |
| _None_ | _Unassigned_ | _idle_ | _No active agents yet._ |

## Current Roles

- _No active roles yet._

## Chat Context

- _No messages yet._
```

## Section Rules

- `Agent Roster`: keep one row per claimed `thing-N` agent.
- `Current Roles`: summarize the active role, scope, and status for each registered agent.
- `Chat Context`: append concise inter-agent messages only. Use the exact shape `thing-1 -> thing-2: message`.

## Manual Editing Guidance

- Preserve the section headings exactly so helper tooling can repair or update the file.
- Keep agent identifiers numeric and monotonic.
- Prefer short role names and short scope statements. They read better in both the roster and the derived current-role list.
- Treat `Current Roles` as generated state when using the helper CLI. Update the roster through `claim` or `set-role`, then let the script rewrite the role summary.
- Do not rewrite history in `Chat Context`. Append new lines instead.

## Example Entries

```markdown
| thing-1 | coordinator | active | break the task into worker-sized chunks |
| thing-2 | implementer | active | own the helper script and tests |
```

```markdown
- `thing-1`: coordinator. Scope: break the task into worker-sized chunks. Status: active.
- `thing-2`: implementer. Scope: own the helper script and tests. Status: active.
```

```markdown
- thing-1 -> thing-2: I claimed the README and skill metadata. Please take the workspace script.
- thing-2 -> thing-1: Script is in place. Review the CLI names before we finalize.
```
