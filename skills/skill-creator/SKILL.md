---
name: skill-creator
description: Create, edit, improve, or audit AgentSkills following the Progressive Disclosure design pattern. Use when creating a new skill from scratch, improving an existing skill, auditing skill quality, or restructuring skill directories (scripts/, references/, assets/). Triggers on: "create a skill", "author a skill", "improve this skill", "audit the skill", "tidy up skill".
---

# Skill Creator

This skill provides the standard workflow for creating effective, context-efficient AgentSkills using Progressive Disclosure.

## Progressive Disclosure Design
1. **Metadata**: Description field in YAML (Always in context).
2. **SKILL.md**: Essential procedural guidance.
3. **References/**: On-demand documentation (schemas, templates).

## Anatomy of a Skill
- [ ] [Anatomy & Spec](references/yaml-spec.md)
- [ ] [Templates](references/skill-template.md)

## Core Workflow
1. **Understand**: Identify concrete user examples.
2. **Plan**: Determine if scripts (`scripts/`), references (`references/`), or assets (`assets/`) are needed.
3. **Initialize**: Use `scripts/init_skill.py`.
4. **Edit**: Implement logic, write SKILL.md.
5. **Package**: Use `scripts/package_skill.py` (Validation required).
6. **Iterate**: Refine based on actual usage performance.

## Best Practices
- **Naming**: `lowercase-hyphen-case`, verb-led.
- **Packaging**: Always run `package_skill.py`. If validation fails, fix the errors—do not bypass.
