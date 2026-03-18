---
name: bytedance-seedance-2-fast
description: Generate videos with ByteDance Jimeng AI 3.0 (720P). Use for T2V, I2I tasks. INCLUDES MANDATORY: Automated Prompt Optimization Workflow.
---

# ByteDance Seedance 2.0 (Video Generation)

Use this skill to transform thematic topics into cinematic 5-10s video clips.

## MANDATORY: Thematic Generation Workflow
If the user provides a *topic* (e.g., "The Terracotta Army"):
1. **Prepare Prompt**: Run `python3 scripts/optimize_prompt.py "<topic>"` to get the template structure.
2. **Expand**: Fill in the `[Camera]`, `[Subject]`, etc., following the [Prompt Formula](references/prompt-formulas.md).
3. **Generate**: Call `python3 scripts/generate_video.py -p "<Finalized Prompt>"` to invoke the Jimeng AI API.

## Cinematic Formula
`[Camera] + [Subject] + [Action] + [Atmosphere] + [Lighting] + [Quality Tags]`

## Usage

```bash
# Workflow: 
# 1. python3 scripts/optimize_prompt.py "Your Topic"
# 2. python3 scripts/generate_video.py -p "<Generated Prompt>" -o output.mp4
```

See [API Docs](references/api-docs.md) for endpoint config.
