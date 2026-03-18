---
name: skill-creator
description: Create, edit, improve, or audit AgentSkills following the Progressive Disclosure design pattern. Use when creating a new skill from scratch, improving an existing skill, auditing skill quality, or restructuring skill directories (scripts/, references/, assets/). Triggers on: "create a skill", "author a skill", "improve this skill", "audit the skill", "tidy up skill".
---

# Skill Creator

This skill provides the standard workflow for creating effective, context-efficient AgentSkills.

## Progressive Disclosure Design Principle

Skills are shared context. Manage them efficiently:

1. **Level 1: Metadata (Name + Description)** - Always in context. Keep the description precise for triggering.
2. **Level 2: SKILL.md body** - Loaded only when the skill triggers. Keep under 500 lines.
3. **Level 3: Bundled Resources** - Loaded *only* when Codex/the agent determines it needs specific details (e.g., schemas, docs, templates).

## Anatomy of a Skill

```
skill-name/
├── SKILL.md (Required: Frontmatter + Instructions)
├── scripts/ (Executable code: Python/Bash)
├── references/ (Docs to be read on-demand)
└── assets/ (Templates, media, boilerplate)
```

## Core Principles

### 1. Concise is Key
Assume the agent is already smart. Only include context it *doesn't* already have. Challenge every paragraph: "Does this justify the token cost?"

### 2. Set Degrees of Freedom
- **High (Text instructions)**: Complex, variable decisions.
- **Medium (Pseudocode/Config)**: Preferred patterns, minor variations.
- **Low (Specific scripts)**: Fragile, mission-critical, consistent execution needed.

### 3. Organize by Load-Pattern
- Move detailed docs, schemas, and long-form examples to `references/`.
- Reference them in `SKILL.md` (e.g., "See [schema.md](references/schema.md) for details").
- The agent will only load these files if it needs the specific info.

## Skill Creation Process

1. **Understand**: Identify concrete user examples.
2. **Plan**: Determine if scripts, references, or assets are needed.
3. **Initialize**: Use `init_skill.py`.
4. **Edit**: Implement logic, write SKILL.md (imperative/infinitive tone).
5. **Package**: Run `package_skill.py` to validate and distribute.
6. **Iterate**: Refine based on actual usage performance.

## Best Practices

- **Naming**: `lowercase-hyphen-case`, verb-led (e.g., `generate-video`).
- **Metadata**: YAML frontmatter only. Include *all* "when to use" trigger context in the `description` field.
- **Versioning**: If a skill supports multiple frameworks/variants, put details in `references/framework-x.md` rather than cramming them into `SKILL.md`.
- **Packaging**: Use `package_skill.py`. It enforces strict validation (YAML syntax, file structure, broken references). If packaging fails, fix the reported errors—do not bypass.

## When to Audit/Clean
- When a skill bloats (>500 lines in SKILL.md).
- When the agent fails to trigger appropriately.
- When resource management is poor (too much info loaded too early).
