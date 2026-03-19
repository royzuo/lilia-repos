---
name: football-tracker
description: "Search and structure real-time football schedules from web sources using a 3-step pipeline: Hybrid Search, Fetch, and LLM Extraction."
---

# Football Tracker (Schedule Parser)

Use this skill to transform unstructured web sports data into structured schedules (JSON).

## The 3-Step Pipeline
1. **Search**: Use `web-hybrid-search -q "<League> schedule"` to find a high-quality data source (e.g., Dongqiudi, 7M).
2. **Fetch**: Use `web_fetch <URL>` on the top-ranking result.
3. **Extract**: Let the Agent reason through the markdown text and perform structural extraction.

## Workflow Instructions
1. Run `web-hybrid-search -q "<League> schedule"`.
2. Inspect results. Select the most "machine-readable" source (e.g., mobile version of sites).
3. Use `web_fetch` on the best source.
4. If extraction is complex, refer to [Parsing Guide](references/parsing-guide.md).

## Usage
- "What matches are happening this weekend for the Premier League?"
- "Track the schedule for Real Madrid for the next 7 days."
