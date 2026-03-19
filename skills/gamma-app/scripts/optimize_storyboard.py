#!/usr/bin/env python3
import sys
import argparse

TEMPLATE = """
[System Instruction: You are a professional educator and storyteller.]

Transform the following topic into a deep, engaging presentation storyboard.

### Structure
- Each slide separated by `---`
- Use headings (#, ##)
- Deepen the "Why" and "How" (not just basic facts)
- Add curiosity hooks and open questions

### Topic
{topic}
"""

def optimize(topic):
    print(TEMPLATE.format(topic=topic))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", help="Topic for the presentation")
    args = parser.parse_args()
    optimize(args.topic)
