#!/usr/bin/env python3
import sys
import argparse

TEMPLATE = """
[System Instruction: You are a professional cinematographer.]

Transform the following topic into a detailed video generation prompt.

### Formula
[Camera] + [Subject] + [Action] + [Atmosphere] + [Lighting] + [Quality Tags]

### Constraints
- Keep it under 400 words.
- Focus on visual details.
- Avoid resolution tags.

### Topic
{topic}
"""

def optimize(topic):
    # In a real agent, this would call an LLM. 
    # For a skill script, we provide the template structure for the Agent to fill in.
    print(TEMPLATE.format(topic=topic))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", help="The topic to optimize")
    args = parser.parse_args()
    optimize(args.topic)
