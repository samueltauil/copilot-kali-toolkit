#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "plugins" / "kali-pentest-toolkit"
AGENTS_DIR = PLUGIN_DIR / "agents"
SKILLS_DIR = PLUGIN_DIR / "skills"


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}


def frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        errors.append(f"{path.relative_to(ROOT)}: missing opening frontmatter delimiter")
        return {}

    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"{path.relative_to(ROOT)}: missing closing frontmatter delimiter")
        return {}

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([a-zA-Z][a-zA-Z0-9-]*):\s*(.+)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def component_paths(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def main() -> int:
    errors: list[str] = []
    plugin_path = PLUGIN_DIR / "plugin.json"
    marketplace_path = ROOT / ".github" / "plugin" / "marketplace.json"
    plugin = load_json(plugin_path, errors)
    marketplace = load_json(marketplace_path, errors)

    if not (ROOT / "LICENSE").is_file():
        errors.append("LICENSE: missing")

    expected_repository = "https://github.com/samueltauil/copilot-kali-toolkit"
    if plugin.get("repository") != expected_repository:
        errors.append("plugin.json: repository must point to the public GitHub repository")
    if plugin.get("homepage") != expected_repository:
        errors.append("plugin.json: homepage must point to the public GitHub repository")

    owner = marketplace.get("owner", {})
    if not isinstance(owner, dict) or owner.get("email") == "security@example.com":
        errors.append("marketplace.json: replace placeholder owner metadata")

    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list) or len(entries) != 1:
        errors.append("marketplace.json: expected exactly one plugin entry")
        entries = []
    elif entries[0].get("version") != plugin.get("version"):
        errors.append("plugin and marketplace versions do not match")

    for field in ("agents", "skills"):
        paths = component_paths(plugin.get(field))
        if not paths:
            errors.append(f"plugin.json: {field} must declare at least one component path")
        for value in paths:
            if not (PLUGIN_DIR / value).is_dir():
                errors.append(f"plugin.json: missing {field} directory: {value}")

    agent_files = sorted(AGENTS_DIR.glob("*.agent.md"))
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    seen_names: set[str] = set()

    for path in agent_files:
        fields = frontmatter(path, errors)
        name = fields.get("name", "")
        for required in ("name", "description", "tools"):
            if required not in fields:
                errors.append(f"{path.relative_to(ROOT)}: missing {required} frontmatter")
        if name and path.name != f"{name}.agent.md":
            errors.append(f"{path.relative_to(ROOT)}: filename does not match agent name {name}")
        if name in seen_names:
            errors.append(f"{path.relative_to(ROOT)}: duplicate component name {name}")
        seen_names.add(name)
        if "## Rules of engagement (mandatory)" not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(ROOT)}: missing mandatory rules of engagement")

    for path in skill_files:
        fields = frontmatter(path, errors)
        name = fields.get("name", "")
        for required in ("name", "description"):
            if required not in fields:
                errors.append(f"{path.relative_to(ROOT)}: missing {required} frontmatter")
        if name and path.parent.name != name:
            errors.append(f"{path.relative_to(ROOT)}: directory does not match skill name {name}")
        if name in seen_names:
            errors.append(f"{path.relative_to(ROOT)}: duplicate component name {name}")
        seen_names.add(name)
        if "## Safety" not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(ROOT)}: missing Safety section")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for count, label in ((len(agent_files), "custom agents"), (len(skill_files), "step by step command workflows")):
        if f"{count} {label}" not in readme:
            errors.append(f"README.md: inventory does not mention {count} {label}")
    for name in seen_names:
        if f"`{name}`" not in readme:
            errors.append(f"README.md: component {name} is not documented")

    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts and path.suffix in {".md", ".json", ".py", ".yml", ".yaml"}:
            text = path.read_text(encoding="utf-8")
            if "\u2014" in text:
                errors.append(f"{path.relative_to(ROOT)}: contains an em dash")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validation passed: {len(agent_files)} agents, {len(skill_files)} skills, version {plugin.get('version')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
