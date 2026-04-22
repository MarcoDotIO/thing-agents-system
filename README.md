# thing-agents-system

Codex skill for coordinating multiple agents through a shared repo-root `collab-workspace.md`.

## What This Repo Contains

- `SKILL.md`: skill instructions for collaborative multi-agent work
- `agents/openai.yaml`: skill metadata for Codex UI discovery
- `collab-workspace.md`: shared project coordination file at the repo root
- `scripts/manage_collab_workspace.py`: helper CLI for claiming `thing-N` identities and logging messages
- `references/collab-workspace-format.md`: canonical workspace format and examples

## Collaboration Model

- Each agent claims the next numeric identity: `thing-1`, `thing-2`, `thing-3`, and so on.
- Agent ownership and scope live in `collab-workspace.md`.
- Inter-agent messages are appended in this exact form: `thing-1 -> thing-2: message`.
- The helper CLI serializes updates with a lock file so concurrent claims do not reuse the same `thing-N` id.

## Example Usage

```bash
python3 scripts/manage_collab_workspace.py ensure
python3 scripts/manage_collab_workspace.py claim --role "coordinator" --scope "break the task into parallel work"
python3 scripts/manage_collab_workspace.py message --from thing-1 --to thing-2 --message "Please take the script and tests."
python3 scripts/manage_collab_workspace.py set-role --agent thing-1 --role "reviewer" --scope "verify the final handoff" --status active
```

If you want Codex to auto-discover this as a local skill, place this folder under `${CODEX_HOME:-$HOME/.codex}/skills/thing-agents-system`.
