#!/usr/bin/env python3
import json
import subprocess
import argparse
import random

HYBRID_SEARCH = "/home/openclaw/.openclaw/workspace/lilia-repos/skills/web-hybrid-search/scripts/hybrid_search.py"
SOURCES_PATH = "/home/openclaw/.openclaw/workspace/openclaw-repos/football-matches/sources.json"

def get_random_league():
    with open(SOURCES_PATH, 'r') as f:
        sources = json.load(f)
    return random.choice(list(sources.keys()))

def run_task(query):
    # If the query seems general, pick a random league to expand recall
    if query in ["general", "important", "all"]:
        league = get_random_league()
        query = f"{league} match schedule"
    
    print(f"Executing Precise Search for: {query}")
    search_cmd = ["python3", HYBRID_SEARCH, "--query", query]
    search_res = subprocess.run(search_cmd, capture_output=True, text=True)
    if search_res.returncode != 0:
        print("Search failed.")
        return

    data = json.loads(search_res.stdout)
    if not data['results']:
        print("No match sources found.")
        return

    # Use top result
    target_url = data['results'][0]['url']
    print(f"Precise Search found best source: {target_url}")

    # Directed Fetch
    print(f"Fetching: {target_url}")
    scrape_res = subprocess.run(["firecrawl", "scrape", target_url], capture_output=True, text=True)
    
    # Output to stdout for Agent Parsing
    print("--- FETCHED CONTENT START ---")
    print(scrape_res.stdout)
    print("--- FETCHED CONTENT END ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", required=True)
    args = parser.parse_args()
    run_task(args.query)
