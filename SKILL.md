---
name: thing-agents-system
description: Coordinate collaborative work across multiple Codex agents through a shared repo-root `collab-workspace.md`, sequential `thing-N` agent names, explicit role ownership, and chat entries formatted as `thing-x -> thing-y: message`. Use when Codex needs to split work across agents, claim responsibilities, hand off tasks, or keep a live multi-agent project log synchronized inside a repository.
---

# Thing Agents System

Use this skill when several Codex agents need one shared source of truth inside the repo.

## Core Workflow

1. Read `collab-workspace.md` before doing substantive work.
2. If the workspace is missing or malformed, run `python3 scripts/manage_collab_workspace.py ensure`.
3. Claim the next available identity with `python3 scripts/manage_collab_workspace.py claim --role "<role>" --scope "<scope>"`.
4. Use the returned `thing-N` name consistently for the rest of the task.
5. Keep `Current Roles` aligned with actual ownership. Before changing scope, run `set-role`.
6. Log directed communication with `python3 scripts/manage_collab_workspace.py message --from thing-1 --to thing-2 --message "..."`.
7. Leave a handoff message in `Chat Context` before pausing, handing work off, or exiting.

## Naming Rules

- Use numeric agent names only: `thing-1`, `thing-2`, `thing-3`, and so on.
- Compute the next name as `max(existing N) + 1`.
- Never recycle or rename an existing agent identifier inside the same workspace.

## File Contract

- Keep the shared workspace at repo root as `collab-workspace.md`.
- Preserve the canonical sections:
  - `Agent Roster`
  - `Current Roles`
  - `Chat Context`
- Use the exact chat format `thing-x -> thing-y: message` with the real assigned agent names substituted in.
- Treat `Agent Roster` and `Current Roles` as structured sections. Prefer the helper script instead of ad hoc edits.

## Coordination Rules

- Claim ownership before editing shared files or taking over a task.
- Keep messages short, concrete, and action-oriented.
- Send a directed message when blocked instead of leaving an ambiguous note.
- Update the prior agent's status or leave a takeover message when inheriting unfinished work.
- Do not delete prior chat entries unless they were duplicated in the current turn.

## References

- Read `references/collab-workspace-format.md` for the canonical markdown layout and manual editing rules.
- Use `python3 scripts/manage_collab_workspace.py --help` for the supported workspace operations.
