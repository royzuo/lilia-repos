---
name: bytedance-seedance-2-fast
description: Generate videos with ByteDance Jimeng AI 3.0 (720P). Use for T2V, I2V, and I2I tasks. Features intelligent prompt optimization workflow.
---

# ByteDance Seedance 2.0 (Video Generation)

Use this skill to transform thematic topics into cinematic 5-10s video clips.

## The Workflow: "Thematic Generation"
1. **Understand Topic**: Agent extracts the core visual theme (e.g., "The Qin Terracotta Army").
2. **Optimize Prompt**: Apply the [Cinematic Formula](references/prompt-formulas.md) to generate a detailed, film-grade prompt.
3. **Generate**: Call `generate_video.py` to invoke the Jimeng AI API.
4. **Deliver**: Provide the MP4 file (or download link) to the user.

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
