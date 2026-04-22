#!/usr/bin/env python3

from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import re
from pathlib import Path

TITLE = "# Collaboration Workspace"
AGENT_RE = re.compile(r"^thing-(\d+)$")


def add_workspace_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("collab-workspace.md"),
        help="Path to the collaboration workspace file.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create and maintain the shared collab-workspace.md file."
    )
    add_workspace_argument(parser)

    subparsers = parser.add_subparsers(dest="command", required=True)

    ensure = subparsers.add_parser(
        "ensure", help="Create or repair the workspace structure."
    )
    add_workspace_argument(ensure)

    claim = subparsers.add_parser(
        "claim", help="Claim the next available thing-N identity."
    )
    add_workspace_argument(claim)
    claim.add_argument("--role", required=True, help="Current role for the new agent.")
    claim.add_argument(
        "--scope", required=True, help="Short scope statement for the new agent."
    )
    claim.add_argument(
        "--status",
        default="active",
        help="Current status for the new agent. Defaults to active.",
    )

    update = subparsers.add_parser(
        "set-role", help="Update the role, scope, or status for an existing agent."
    )
    add_workspace_argument(update)
    update.add_argument("--agent", required=True, help="Existing thing-N agent id.")
    update.add_argument("--role", required=True, help="Updated role name.")
    update.add_argument("--scope", required=True, help="Updated scope statement.")
    update.add_argument("--status", required=True, help="Updated status value.")

    message = subparsers.add_parser(
        "message", help="Append a chat entry to the workspace log."
    )
    add_workspace_argument(message)
    message.add_argument("--from", dest="from_agent", required=True)
    message.add_argument("--to", dest="to_agent", required=True)
    message.add_argument("--message", required=True)

    return parser.parse_args()


def normalize_cell(value: str) -> str:
    return " ".join(value.strip().replace("|", "/").split())


def lock_path_for(workspace: Path) -> Path:
    return workspace.with_name(f".{workspace.name}.lock")


@contextmanager
def workspace_lock(workspace: Path):
    lock_path = lock_path_for(workspace)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def parse_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^## (.+?)\n", text, flags=re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[name] = text[start:end].strip("\n")
    return sections


def parse_roster(section_text: str) -> list[dict[str, str]]:
    agents: list[dict[str, str]] = []
    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        columns = [column.strip() for column in line.strip("|").split("|")]
        if len(columns) < 4:
            continue
        agent, role, status, scope = columns[:4]
        if agent == "Agent" or set(agent) == {"-"}:
            continue
        if not AGENT_RE.fullmatch(agent):
            continue
        agents.append(
            {
                "agent": agent,
                "role": role,
                "status": status,
                "scope": scope,
            }
        )
    agents.sort(key=lambda item: int(AGENT_RE.fullmatch(item["agent"]).group(1)))
    return agents


def parse_chat(section_text: str) -> list[str]:
    lines = []
    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if not line or line == "- _No messages yet._":
            continue
        if line.startswith("- "):
            lines.append(line)
    return lines


def format_roster(agents: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Agent | Role | Status | Scope |",
        "| --- | --- | --- | --- |",
    ]
    if not agents:
        lines.append("| _None_ | _Unassigned_ | _idle_ | _No active agents yet._ |")
        return lines
    for agent in agents:
        lines.append(
            "| {agent} | {role} | {status} | {scope} |".format(
                agent=agent["agent"],
                role=normalize_cell(agent["role"]),
                status=normalize_cell(agent["status"]),
                scope=normalize_cell(agent["scope"]),
            )
        )
    return lines


def format_current_roles(agents: list[dict[str, str]]) -> list[str]:
    if not agents:
        return ["- _No active roles yet._"]
    return [
        "- `{agent}`: {role}. Scope: {scope}. Status: {status}.".format(
            agent=agent["agent"],
            role=normalize_cell(agent["role"]),
            scope=normalize_cell(agent["scope"]),
            status=normalize_cell(agent["status"]),
        )
        for agent in agents
    ]


def format_chat(messages: list[str]) -> list[str]:
    if not messages:
        return ["- _No messages yet._"]
    return messages


def compose_workspace(agents: list[dict[str, str]], messages: list[str]) -> str:
    lines = [TITLE, ""]
    lines.extend(["## Agent Roster", ""])
    lines.extend(format_roster(agents))
    lines.extend(["", "## Current Roles", ""])
    lines.extend(format_current_roles(agents))
    lines.extend(["", "## Chat Context", ""])
    lines.extend(format_chat(messages))
    lines.append("")
    return "\n".join(lines)


def load_workspace(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], []
    text = path.read_text(encoding="utf-8")
    sections = parse_sections(text)
    roster = parse_roster(sections.get("Agent Roster", ""))
    chat = parse_chat(sections.get("Chat Context", ""))
    return roster, chat


def write_workspace(path: Path, agents: list[dict[str, str]], messages: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_text(compose_workspace(agents, messages), encoding="utf-8")
    tmp_path.replace(path)


def next_agent_name(agents: list[dict[str, str]]) -> str:
    if not agents:
        return "thing-1"
    last_agent = agents[-1]["agent"]
    last_number = int(AGENT_RE.fullmatch(last_agent).group(1))
    return f"thing-{last_number + 1}"


def require_known_agent(agents: list[dict[str, str]], agent_name: str, label: str) -> None:
    if not AGENT_RE.fullmatch(agent_name):
        raise SystemExit(f"Invalid {label}: {agent_name}")
    known_agents = {agent["agent"] for agent in agents}
    if agent_name not in known_agents:
        raise SystemExit(f"Unknown {label}: {agent_name}")


def claim_agent(
    agents: list[dict[str, str]], role: str, scope: str, status: str
) -> str:
    agent_name = next_agent_name(agents)
    agents.append(
        {
            "agent": agent_name,
            "role": role,
            "status": status,
            "scope": scope,
        }
    )
    agents.sort(key=lambda item: int(AGENT_RE.fullmatch(item["agent"]).group(1)))
    return agent_name


def update_agent(
    agents: list[dict[str, str]], agent_name: str, role: str, scope: str, status: str
) -> None:
    for agent in agents:
        if agent["agent"] == agent_name:
            agent["role"] = role
            agent["scope"] = scope
            agent["status"] = status
            return
    raise SystemExit(f"Unknown agent: {agent_name}")


def append_message(messages: list[str], from_agent: str, to_agent: str, message: str) -> None:
    text = " ".join(message.strip().split())
    if not text:
        raise SystemExit("Message cannot be empty.")
    messages.append(f"- {from_agent} -> {to_agent}: {text}")


def main() -> None:
    args = parse_args()
    with workspace_lock(args.workspace):
        agents, messages = load_workspace(args.workspace)

        if args.command == "ensure":
            write_workspace(args.workspace, agents, messages)
            return

        if args.command == "claim":
            agent_name = claim_agent(agents, args.role, args.scope, args.status)
            write_workspace(args.workspace, agents, messages)
            print(agent_name)
            return

        if args.command == "set-role":
            update_agent(agents, args.agent, args.role, args.scope, args.status)
            write_workspace(args.workspace, agents, messages)
            return

        if args.command == "message":
            require_known_agent(agents, args.from_agent, "sender")
            require_known_agent(agents, args.to_agent, "recipient")
            append_message(messages, args.from_agent, args.to_agent, args.message)
            write_workspace(args.workspace, agents, messages)
            return

        raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
