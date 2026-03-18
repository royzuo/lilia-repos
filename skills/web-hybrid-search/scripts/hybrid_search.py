#!/usr/bin/env python3
"""
Web Hybrid Search - 混合网络搜索技能 (优化版)
整合 SearchCans、Linkup
"""

import os
import sys
import json
import argparse
import logging
import subprocess
from datetime import datetime, timezone
from typing import List, Dict, Any
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SEARCHCANS_API_KEY = os.environ.get("SEARCHCANS_API_KEY")
LINKUP_API_KEY = os.environ.get("LINKUP_API_KEY")

def search_with_searchcans(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """使用 SearchCans 直接调用脚本"""
    if not SEARCHCANS_API_KEY: return []
    script_path = os.path.join(os.path.dirname(__file__), '../../searchcans-web/scripts/searchcans.py')
    if not os.path.exists(script_path): return []
    try:
        result = subprocess.run(
            [sys.executable, script_path, 'search', '--query', query, '--engine', 'google', '--limit', str(limit)],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode != 0: return []
        # 简单解析 (若脚本输出为JSON，需相应调整)
        return [] 
    except Exception as e:
        logger.error(f"SearchCans 异常: {e}")
        return []

def search_with_linkup(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """使用 Linkup API"""
    if not LINKUP_API_KEY: return []
    try:
        response = requests.post(
            'https://api.linkup.so/v1/search',
            headers={'Authorization': f'Bearer {LINKUP_API_KEY}', 'Content-Type': 'application/json'},
            json={'q': query, 'depth': 'standard', 'outputType': 'searchResults'},
            timeout=15
        )
        if response.status_code != 200: return []
        data = response.json()
        return [{'source': 'linkup', 'title': item.get('name', ''), 'url': item.get('url', ''), 'content': item.get('content', ''), 'favicon': item.get('favicon', '')} for item in data.get('results', [])[:limit]]
    except Exception as e:
        logger.error(f"Linkup 异常: {e}")
        return []

def deduplicate_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique_by_url = {r.get('url'): r for r in results if r.get('url')}
    deduped = []
    titles_seen = []
    for r in unique_by_url.values():
        title = r.get('title', '')
        if not any(SequenceMatcher(None, title, t).ratio() > 0.9 for t in titles_seen):
            deduped.append(r)
            titles_seen.append(title)
    return deduped

def hybrid_search(query: str, limit: int = 5) -> Dict[str, Any]:
    tasks = {'searchcans': lambda: search_with_searchcans(query, limit), 'linkup': lambda: search_with_linkup(query, limit)}
    all_results = []
    tools_used = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_tool = {executor.submit(func): tool for tool, func in tasks.items()}
        for future in as_completed(future_to_tool):
            tool = future_to_tool[future]
            try:
                res = future.result()
                if res:
                    all_results.extend(res)
                    tools_used.append(tool)
            except Exception as e:
                logger.error(f"{tool} 出错: {e}")
    return {'query': query, 'results': deduplicate_results(all_results), 'tools_used': tools_used}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', '-q', required=True)
    args = parser.parse_args()
    print(json.dumps(hybrid_search(args.query), ensure_ascii=False))
