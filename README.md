# Kali Linux Security Toolkit for GitHub Copilot CLI

A GitHub Copilot CLI plugin that adds custom agents and skills for the
security and penetration testing tools that ship with Kali Linux. Instead of
typing raw nmap or sqlmap flags from memory, you describe what you're trying
to do and Copilot picks the right agent, follows a sane methodology, and
gives you the actual commands for the tools installed on your system.

This is built for people running Copilot CLI directly on a Kali box (a VM,
WSL, or bare metal) during authorized penetration tests, CTFs, or lab work
such as OSCP/HTB/TryHackMe.

## Why use this on Kali

Kali ships with hundreds of tools and most people only remember the flags for
the ten or so they use every week. This toolkit fixes that in three concrete
ways:

- **Less flag hunting.** Ask for "an nmap scan of this host" and get the
  right progression (host discovery, full port sweep, service/version scan,
  UDP sample) instead of guessing which of the fifty nmap options you need.
- **A methodology, not just a tool.** The `pentest-orchestrator` agent keeps
  an engagement moving through recon, scanning, exploitation, and reporting
  in the right order, and delegates to the specialist agent for each phase.
- **Built-in guardrails.** Every agent asks for confirmed scope and
  authorization before running anything active, defaults to the least
  intrusive option first, and reminds you to redact secrets when writing
  things up. This matters if you are new to pentesting and don't want to
  accidentally scan or brute-force something out of scope.

It also saves time on the boring parts: turning a pile of Nmap/Nikto/Hydra
output into a clean, CVSS-scored report is handled by the `pentest-reporter`
agent and the `pentest-report-writing` skill.

## What's in the box

```
.github/plugin/marketplace.json          marketplace manifest
plugins/kali-pentest-toolkit/
  plugin.json                            plugin manifest
  agents/*.agent.md                      14 custom agents, one per tool category
  skills/*/SKILL.md                      9 step by step command workflows
```

### Agents

| Agent | Covers | Main tools |
|---|---|---|
| `pentest-orchestrator` | Full engagement planning | Delegates to every agent below |
| `osint-recon` | Information gathering | theHarvester, Recon-ng, Amass, Sublist3r, dnsrecon, Shodan/Censys |
| `network-scanner` | Host and service discovery | Nmap, Masscan, arp-scan, netdiscover, enum4linux-ng |
| `vuln-assessment` | Vulnerability scanning | Nikto, Nuclei, OpenVAS/Greenbone, Legion, searchsploit, WPScan |
| `web-app-pentester` | Web application testing | Burp Suite, ZAP, gobuster, ffuf, sqlmap, XSStrike, dalfox |
| `password-auditor` | Password and hash attacks | Hydra, Medusa, John the Ripper, Hashcat, CeWL, Crunch |
| `wireless-auditor` | Wi-Fi assessments | aircrack-ng, Wifite, Kismet, Reaver, hcxdumptool, Bettercap |
| `exploitation-engineer` | Exploitation | Metasploit, msfvenom, searchsploit, BeEF |
| `ad-specialist` | Active Directory attacks | Impacket, CrackMapExec/NetExec, Responder, BloodHound, Evil-WinRM |
| `post-exploitation` | Privilege escalation and pivoting | LinPEAS/WinPEAS, Mimikatz, Chisel, Ligolo-ng, Meterpreter |
| `network-sniffer` | Traffic capture and MITM | Wireshark, tcpdump, Ettercap, Bettercap, mitmproxy |
| `forensics-investigator` | Digital forensics | Autopsy, The Sleuth Kit, Volatility3, Binwalk, Plaso |
| `reverse-engineer` | Binary analysis | Ghidra, radare2/Cutter, GDB with GEF/pwndbg, objdump |
| `pentest-reporter` | Report writing | Turns findings into a CVSS-scored client report |

### Skills

Concrete runbooks with real commands: `nmap-recon`, `web-content-discovery`,
`sqlmap-injection-testing`, `password-cracking`, `wifi-handshake-crack`,
`msf-exploitation`, `ad-enumeration`, `memory-forensics`,
`pentest-report-writing`.

## Requirements

- Kali Linux (or any Linux distro with the equivalent tools installed).
- [GitHub Copilot CLI](https://docs.github.com/copilot/how-tos/use-copilot-agents/use-copilot-cli)
  installed and logged in (`copilot`, then `/login` if needed).
- The actual security tools referenced by each agent (nmap, sqlmap, hydra,
  aircrack-ng, and so on). Kali installs most of these by default; anything
  missing can be added with `apt install <package>`.

## Install

The recommended way is through the marketplace, once the repo is public:

```shell
copilot plugin marketplace add samueltauil/copilot-kali-toolkit
copilot plugin install kali-pentest-toolkit@copilot-kali-toolkit
```

You can also install straight from a local clone, which is useful if you
want to edit the agents yourself:

```shell
git clone https://github.com/samueltauil/copilot-kali-toolkit.git
copilot plugin install ./copilot-kali-toolkit/plugins/kali-pentest-toolkit
```

Restart Copilot CLI (or start a new session) after installing.

## Configure

Nothing needs to be configured to get started. Two things worth knowing:

- **Restricting tool access.** Each agent's frontmatter already lists only
  the tools it needs (mostly `bash`, `view`, `edit`, `create`, `grep`,
  `glob`, with `web_search`/`web_fetch` added for `osint-recon` only). If
  your environment needs tighter restrictions, edit the `tools:` line in the
  relevant `agents/*.agent.md` file.
- **Adding your own scope defaults.** If you always test the same lab
  range or client environment, add a short note to your project's
  `AGENTS.md` or `.github/copilot-instructions.md` describing the default
  authorized scope so the orchestrator doesn't have to ask every time.

## Update

If you installed from the marketplace:

```shell
copilot plugin marketplace update copilot-kali-toolkit
copilot plugin update kali-pentest-toolkit
```

If you installed from a local clone, pull the latest changes and reinstall:

```shell
cd copilot-kali-toolkit && git pull
copilot plugin install ./plugins/kali-pentest-toolkit
```

## Verify it loaded

```shell
copilot plugin list
```

Then, inside an interactive session:

```
/agent
/skills list
```

You should see the 14 agents and 9 skills listed above.

## Example prompts

```
Use the pentest-orchestrator agent to plan an assessment of 10.10.10.0/24. I have signed authorization for this range.

Use the nmap-recon skill against 10.10.10.5.

Use the web-app-pentester agent to enumerate content on https://staging.example.com, which is in scope for this engagement.
```

## A note on scope and authorization

Every agent in this toolkit expects you to confirm you have written
authorization and a defined scope before it runs anything active. If you
ask it to test something and haven't mentioned authorization, it will ask
before proceeding. This toolkit is meant for lawful penetration testing,
CTFs, and your own lab environments, not for testing systems you don't own
or have permission to test.

## Contributing

Pull requests that add coverage for another Kali tool category, fix a
command, or improve a skill's accuracy are welcome. See
[`.github/copilot-instructions.md`](.github/copilot-instructions.md) for the
conventions this repo follows.

## License

MIT. Tool names mentioned throughout (Nmap, Metasploit, Kali Linux, and so
on) belong to their respective projects. This project is not affiliated
with or endorsed by Offensive Security.
