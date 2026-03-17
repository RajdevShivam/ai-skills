---
name: add-skill
description: Create a new Agent Skill in the shared skills directory. Use when the user wants to add, create, or register a new skill for Claude Code and Crush.
argument-hint: <skill-name> [description]
---

# Add Skill - Create New Shared Agent Skills

Create new skills in the shared directory so both Claude Code and Crush can use them.

## Shared Skills Location

All skills live in: `C:\Users\shiva\ai-skills\`

This directory is read by:
- **Claude Code** via junction at `C:\Users\shiva\.claude\skills\`
- **Crush** via `skills_paths` in `C:\Users\shiva\AppData\Local\crush\crush.json`

## How to Create a Skill

When the user says `$ARGUMENTS`, interpret the first word as the skill name and the rest as the description.

1. Create directory: `C:\Users\shiva\ai-skills\<skill-name>\`
2. Create `SKILL.md` inside with this template:

```markdown
---
name: <skill-name>
description: <description of what this skill does and when to activate it>
argument-hint: [args]
---

# <Skill Title>

<Instructions for what the agent should do when this skill is invoked>
```

## Rules

- Skill name must be lowercase alphanumeric with hyphens only (e.g., `my-skill`)
- Name in frontmatter MUST match the directory name exactly
- Description should explain WHEN to activate (triggers), not just WHAT it does
- Keep instructions concise and actionable
- Do NOT add skills anywhere else - always use `C:\Users\shiva\ai-skills\`

## Existing Skills

Check what's already installed:
```bash
ls C:\Users\shiva\ai-skills\
```

## After Creating

Tell the user: "Skill `<name>` created. Available in both Claude Code (`/<name>`) and Crush."
