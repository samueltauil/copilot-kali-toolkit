# Copilot instructions for copilot-kali-toolkit

This repository is a **GitHub Copilot CLI plugin marketplace**: it packages a set of
custom agents and skills (`plugins/kali-pentest-toolkit/`) that give Copilot CLI
expertise in the security/penetration-testing tool categories shipped with Kali
Linux (OSINT, scanning, vulnerability analysis, web app testing, password
attacks, wireless auditing, exploitation, Active Directory attacks,
post-exploitation, sniffing/MITM, forensics, reverse engineering, reporting).

## Repository layout
- `.github/plugin/marketplace.json`: marketplace manifest, lists the plugin(s) in this repo.
- `plugins/kali-pentest-toolkit/plugin.json`: legacy-format plugin manifest (`agents`, `skills` component paths).
- `plugins/kali-pentest-toolkit/agents/*.agent.md`: one custom agent per Kali tool category.
- `plugins/kali-pentest-toolkit/skills/*/SKILL.md`: concrete, copy-pasteable command workflows for common tasks.

## Conventions when editing or adding content
- Every agent body must end with the **Rules of engagement** safety block:
  authorization/scope required, least-intrusive-technique-first, no
  out-of-scope/DoS actions, and redaction of secrets in examples. Every skill
  must include a `## Safety` section tailored to its workflow.
- Agent frontmatter fields: `name` (kebab-case), `description` (states expertise +
  concrete trigger words so Copilot can auto-select the agent), `tools` (restrict
  to only what the agent needs: `bash`, `view`, `edit`, `create`, `grep`, `glob`,
  plus `web_search`/`web_fetch` for OSINT-style agents, `task` for the orchestrator).
- Skill frontmatter fields: `name`, `description` only. Skill bodies are
  step-by-step runbooks with real command-line examples for the actual Kali
  package/binary names (verify tool/flag names before adding new ones).
- Keep new tool coverage aligned to real Kali Linux tool categories/menu groups
  (Information Gathering, Vulnerability Analysis, Web Application Analysis,
  Database Assessment, Password Attacks, Wireless Attacks, Reverse Engineering,
  Exploitation Tools, Sniffing & Spoofing, Post Exploitation, Forensics,
  Reporting Tools, Social Engineering Tools) rather than inventing tools.
- After adding/renaming an agent or skill directory, update `README.md`'s
  coverage table and bump `version` in both `plugin.json` and `marketplace.json`.

## Validation
There is no build step. Run `python3 scripts/validate.py` after every content
or manifest change. It validates JSON, component paths, frontmatter, unique
names, safety sections, metadata, version alignment, and README inventory.
