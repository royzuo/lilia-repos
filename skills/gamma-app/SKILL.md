---
name: gamma-app
description: Generate presentations/docs via Gamma.app API. Includes mandatory storyboard optimization workflow for high-depth content.
---

# Gamma.app Presentation Generator

Use this skill to transform topics into deep, engaging presentations.

## MANDATORY: Storyboard Optimization Workflow
If the user provides a *topic*:
1. **Optimize Outline**: Run `python3 scripts/optimize_storyboard.py "<topic>"` to create a structured Markdown storyboard.
2. **Deepen**: Ensure the storyboard hits the "Why" and "How" (scientific logic, paradoxical questions).
3. **Generate**: Run `python3 scripts/gamma_builder.py <storyboard_file>`.

## Key Principles
- **Hard Breaks**: Slides MUST be separated by `---` on a new line.
- **Deep Engagement**: Don't just list facts. Add curiosity hooks and open questions.
- **Visual Structure**: Break text with lists/bold text.

## Usage

```bash
# Workflow:
# 1. python3 scripts/optimize_storyboard.py "Your Topic" > storyboard.md
# 2. python3 scripts/gamma_builder.py storyboard.md
```

See [Markdown Guide](references/markdown-guide.md) for structure best practices.
