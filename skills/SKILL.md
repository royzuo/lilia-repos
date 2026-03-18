---
name: bytedance-seedance-2-fast
description: Generate videos with ByteDance Jimeng AI 3.0 (720P). Use for T2V, I2V, and I2I tasks. INCLUDES MANDATORY: Prompt Optimization Workflow for thematic inputs.
---

# ByteDance Seedance 2.0 (Video Generation)

Use this skill to transform thematic topics into cinematic 5-10s video clips.

## MANDATORY: Thematic Generation Workflow
If the user provides a *topic* (e.g., "The Terracotta Army") instead of a direct video description:
1. **Load Template**: Use `references/prompt-template.txt`.
2. **Optimize**: Replace `{{TOPIC}}` in the template with the user's input, and expand it following the [Prompt Formula](references/prompt-formulas.md).
3. **Generate**: Call `generate_video.py` using the resulting optimized prompt.

## Cinematic Formula
`[Camera] + [Subject] + [Action] + [Atmosphere] + [Lighting] + [Quality Tags]`

*   **Camera**: Low-angle tracking, wide shot, close-up, etc.
*   **Subject**: Clear, descriptive nouns (e.g., "Terracotta Army").
*   **Action**: Dynamic movement (e.g., "dust dancing", "columns moving").
*   **Atmosphere**: Mood-setting (e.g., "solemn", "epic").
*   **Lighting**: Specific sources (e.g., "chiaroscuro", "dramatic sunset").
*   **Quality Tags**: Cinematic texture, authentic materials, masterful composition.

## Usage

```bash
# Basic usage
python3 scripts/generate_video.py -p "<Optimized Prompt>" -o output.mp4
```

See [API Docs](references/api-docs.md) for endpoint config, error handling, and resolution/duration specs.
