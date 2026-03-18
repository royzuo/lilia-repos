#!/usr/bin/env python3
"""
Web Hybrid Search - 混合网络搜索技能 (优化并行版)
整合 SearchCans、Linkup 和 web_search
"""

import os
import sys
import json
import argparse
import logging
import subprocess
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Keys
SEARCHCANS_API_KEY = os.environ.get("SEARCHCANS_API_KEY")
LINKUP_API_KEY = os.environ.get("LINKUP_API_KEY")

def search_with_searchcans(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """使用 SearchCans 进行搜索"""
    if not SEARCHCANS_API_KEY:
        return []
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), 
                                   '../../searchcans-web/scripts/searchcans.py')
        
        result = subprocess.run(
            ['python3', script_path, 'search', 
             '--query', query, 
             '--engine', 'google',
             '--limit', str(limit)],
            capture_output=True,
            text=True,
            timeout=15 # 增加超时限制
        )
        
        if result.returncode != 0:
            logger.error(f"SearchCans 执行失败: {result.stderr}")
            return []
        
        results = []
        lines = result.stdout.strip().split('\n')
        current_title = None
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith('- '):
                current_title = line[2:].strip()
            elif line.startswith('http') and current_title:
                results.append({
                    'source': 'searchcans',
                    'title': current_title,
                    'url': line,
                    'content': '',
                    'favicon': ''
                })
                current_title = None
        return results
    except Exception as e:
        logger.error(f"SearchCans 异常: {e}")
        return []

def search_with_linkup(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """使用 Linkup 进行搜索"""
    if not LINKUP_API_KEY:
        return []
    
    try:
        import requests
        response = requests.post(
            'https://api.linkup.so/v1/search',
            headers={
                'Authorization': f'Bearer {LINKUP_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'q': query,
                'depth': 'standard',
                'outputType': 'searchResults'
            },
            timeout=15
        )
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        return [{
            'source': 'linkup',
            'title': item.get('name', ''),
            'url': item.get('url', ''),
            'content': item.get('content', ''),
            'favicon': item.get('favicon', '')
        } for item in data.get('results', [])[:limit]]
    except Exception as e:
        logger.error(f"Linkup 异常: {e}")
        return []

def search_with_web_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """使用 OpenClaw CLI 调用 web_search"""
    try:
        # 假设 openclaw CLI 在 PATH 中
        result = subprocess.run(
            ['openclaw', 'web_search', '--query', query, '--count', str(limit)],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode != 0:
            return []
        
        # 假设 OpenClaw CLI 输出 JSON，或者需要解析文本
        data = json.loads(result.stdout)
        results = []
        for item in data:
            results.append({
                'source': 'web_search',
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'content': item.get('snippet', ''),
                'favicon': ''
            })
        return results
    except Exception as e:
        logger.error(f"web_search 异常: {e}")
        return []

def deduplicate_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique_by_url = {}
    for r in results:
        url = r.get('url', '')
        if url and url not in unique_by_url:
            unique_by_url[url] = r
    
    deduped = []
    titles_seen = []
    
    for r in unique_by_url.values():
        title = r.get('title', '')
        if not any(SequenceMatcher(None, title, t).ratio() > 0.9 for t in titles_seen):
            deduped.append(r)
            titles_seen.append(title)
            
    return deduped

def hybrid_search(query: str, limit: int = 5) -> Dict[str, Any]:
    logger.info(f"开始并行混合搜索：{query}")
    
    # 建立任务字典
    tasks = {
        'searchcans': lambda: search_with_searchcans(query, limit),
        'linkup': lambda: search_with_linkup(query, limit),
        'web_search': lambda: search_with_web_search(query, limit)
    }
    
    all_results = []
    tools_used = []
    
    # 并行执行
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_tool = {executor.submit(func): tool for tool, func in tasks.items()}
        for future in as_completed(future_to_tool):
            tool = future_to_tool[future]
            try:
                res = future.result()
                if res:
                    all_results.extend(res)
                    tools_used.append(tool)
            except Exception as e:
                logger.error(f"{tool} 执行出错: {e}")
                
    # 排序优先级
    priority = {'linkup': 0, 'web_search': 1, 'searchcans': 2}
    deduped = deduplicate_results(all_results)
    sorted_results = sorted(deduped, key=lambda x: priority.get(x.get('source', ''), 99))
    
    return {
        'query': query,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'tools_used': tools_used,
        'total_results': len(sorted_results),
        'results': sorted_results
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', '-q', required=True)
    parser.add_argument('--limit', '-l', type=int, default=5)
    parser.add_argument('--output', '-o')
    args = parser.parse_args()
    
    results = hybrid_search(args.query, args.limit)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
