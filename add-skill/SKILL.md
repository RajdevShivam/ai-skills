---
name: add-skill
description: Create a new Agent Skill in the shared skills directory. Use when the user wants to add, create, or register a new skill for Claude Code and Crush.
argument-hint: <skill-name> [description]
---

# Add Skill - Create New Shared Agent Skills

Create new skills in the shared `ai-skills` git repo so they sync across all machines.

## Skills Repo Location (Platform-Dependent)

The `ai-skills` repo is cloned locally and symlinked/junctioned into Claude Code's skills directory.

| Platform | Skills repo | Claude Code reads from |
|----------|-------------|------------------------|
| **Windows** | `C:\Users\shiva\ai-skills\` | `C:\Users\shiva\.claude\skills\` (junction) |
| **Linux/VPS** | `~/ai-skills/` | `~/.claude/skills/` (symlink) |

Crush on Windows also reads via `skills_paths` in `C:\Users\shiva\AppData\Local\crush\crush.json`.

**To determine which platform you're on**, check if `C:\Users\shiva\ai-skills\` exists. If not, use `~/ai-skills/`.

## How to Create a Skill

When the user says `$ARGUMENTS`, interpret the first word as the skill name and the rest as the description.

1. Resolve the skills root directory for the current platform
2. Create directory: `<skills-root>/<skill-name>/`
3. Create `SKILL.md` inside with this template:

```markdown
---
name: <skill-name>
description: <description of what this skill does and when to activate it>
argument-hint: [args]
---

# <Skill Title>

<Instructions for what the agent should do when this skill is invoked>
```

4. After creating, commit and push to git so it syncs everywhere:

```bash
cd <skills-root>
git add <skill-name>/
git commit -m "add skill: <skill-name>"
git push
```

## Rules

- Skill name must be lowercase alphanumeric with hyphens only (e.g., `my-skill`)
- Name in frontmatter MUST match the directory name exactly
- Description should explain WHEN to activate (triggers), not just WHAT it does
- Keep instructions concise and actionable
- Always commit + push after creating or modifying a skill

## Existing Skills

Check what's already installed:
```bash
ls <skills-root>
```

## After Creating

Tell the user: "Skill `<name>` created and pushed. Pull on other machines with `cd ~/ai-skills && git pull`."

## New Machine Setup (Linux/VPS)

If the machine doesn't have the skills repo yet:
```bash
git clone https://github.com/RajdevShivam/ai-skills.git ~/ai-skills
bash ~/ai-skills/setup.sh
```

`setup.sh` symlinks each skill folder individually into `~/.claude/skills/`, preserving any plugin-managed skills already there (e.g. Superpowers GWS skills).

After adding a new skill on any machine, on other machines run:
```bash
cd ~/ai-skills && git pull && bash setup.sh
```
