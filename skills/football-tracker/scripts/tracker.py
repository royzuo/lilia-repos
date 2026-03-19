#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

def tracker_run(query):
    # 1. Search
    print(f"Searching: {query}")
    search_cmd = ["python3", "/home/openclaw/.openclaw/workspace/lilia-repos/skills/web-hybrid-search/scripts/hybrid_search.py", "--query", query]
    search_res = subprocess.run(search_cmd, capture_output=True, text=True)
    if search_res.returncode != 0: return "Search failed"
    
    data = json.loads(search_res.stdout)
    if not data['results']: return "No results found"
    
    target_url = data['results'][0]['url']
    
    # 2. Fetch via Firecrawl
    print(f"Scraping: {target_url}")
    scrape_res = subprocess.run(["firecrawl", "scrape", target_url], capture_output=True, text=True)
    if scrape_res.returncode != 0: return "Scrape failed"
    
    # 3. Output to stdout for Agent LLM Parsing
    print("--- RAW DATA START ---")
    print(scrape_res.stdout)
    print("--- RAW DATA END ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", required=True)
    args = parser.parse_args()
    tracker_run(args.query)
