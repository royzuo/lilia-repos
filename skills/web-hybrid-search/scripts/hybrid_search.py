#!/usr/bin/env python3
"""
Web Hybrid Search - 混合网络搜索技能
整合 SearchCans、Linkup 和 web_search 三个检索工具
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
        logger.warning("SEARCHCANS_API_KEY 未设置，跳过 SearchCans")
        return []
    
    logger.info("🔍 使用 SearchCans 搜索...")
    
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
            timeout=30
        )
        
        if result.returncode != 0:
            logger.error(f"SearchCans 执行失败：{result.stderr}")
            return []
        
        # 解析输出
        results = []
        lines = result.stdout.strip().split('\n')
        current_title = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
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
        
        logger.info(f"SearchCans 返回 {len(results)} 条结果")
        return results
        
    except Exception as e:
        logger.error(f"SearchCans 搜索失败：{e}")
        return []


def search_with_linkup(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """使用 Linkup 进行搜索"""
    if not LINKUP_API_KEY:
        logger.warning("LINKUP_API_KEY 未设置，跳过 Linkup")
        return []
    
    logger.info("🔍 使用 Linkup 搜索...")
    
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
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Linkup API 失败：{response.status_code}")
            return []
        
        data = response.json()
        results = []
        
        for item in data.get('results', [])[:limit]:
            results.append({
                'source': 'linkup',
                'title': item.get('name', ''),
                'url': item.get('url', ''),
                'content': item.get('content', ''),
                'favicon': item.get('favicon', '')
            })
        
        logger.info(f"Linkup 返回 {len(results)} 条结果")
        return results
        
    except Exception as e:
        logger.error(f"Linkup 搜索失败：{e}")
        return []


def search_with_web_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """使用 web_search（通过 OpenClaw）"""
    logger.info("🔍 使用 web_search 搜索...")
    
    try:
        # 使用 web_search 工具
        from sessions_send import sessions_send
        
        # 这里我们模拟调用 web_search
        # 实际使用时需要调用 OpenClaw 的 web_search 工具
        import requests
        
        # 使用 Brave Search API（如果可用）
        # 或者使用其他搜索服务
        results = []
        
        logger.info("web_search 需要 OpenClaw 环境，返回空结果")
        return results
        
    except Exception as e:
        logger.error(f"web_search 失败：{e}")
        return []


def similarity(a: str, b: str) -> float:
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def deduplicate_results(results: List[Dict[str, Any]], threshold: float = 0.9) -> List[Dict[str, Any]]:
    """去重结果"""
    if not results:
        return []
    
    # 首先按 URL 去重
    url_seen = set()
    unique_by_url = []
    
    for r in results:
        url = r.get('url', '')
        if url and url not in url_seen:
            url_seen.add(url)
            unique_by_url.append(r)
    
    # 然后按标题相似度去重
    deduped = []
    for r in unique_by_url:
        title = r.get('title', '')
        is_duplicate = False
        
        for existing in deduped:
            if similarity(title, existing.get('title', '')) > threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            deduped.append(r)
    
    return deduped


def sort_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """按照 Linkup -> web_search -> SearchCans 的顺序排序"""
    priority = {'linkup': 0, 'web_search': 1, 'searchcans': 2}
    return sorted(results, key=lambda x: priority.get(x.get('source', ''), 99))


def hybrid_search(query: str, limit: int = 5, min_results: int = 5) -> Dict[str, Any]:
    """
    混合搜索主函数
    
    Args:
        query: 搜索关键词
        limit: 每个工具的最大结果数
        min_results: 最小结果数阈值
    
    Returns:
        整合后的搜索结果
    """
    logger.info(f"开始混合搜索：{query}")
    logger.info(f"参数：limit={limit}, min_results={min_results}")
    
    all_results = []
    tools_used = []
    
    # Step 1: 优先使用 SearchCans
    searchcans_results = search_with_searchcans(query, limit)
    all_results.extend(searchcans_results)
    if searchcans_results:
        tools_used.append('searchcans')
    
    # Step 2: 选择 Linkup 或 web_search（优先 Linkup）
    if len(all_results) < min_results:
        linkup_results = search_with_linkup(query, limit)
        all_results.extend(linkup_results)
        if linkup_results:
            tools_used.append('linkup')
    
    # Step 3: 如果结果仍不足，使用 web_search 补充
    if len(all_results) < min_results:
        web_results = search_with_web_search(query, limit)
        all_results.extend(web_results)
        if web_results:
            tools_used.append('web_search')
    
    # 去重
    deduped_results = deduplicate_results(all_results)
    
    # 排序
    sorted_results = sort_results(deduped_results)
    
    # 构建输出
    output = {
        'query': query,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'tools_used': tools_used,
        'total_results': len(sorted_results),
        'results': sorted_results
    }
    
    logger.info(f"搜索完成：共 {len(sorted_results)} 条结果，使用工具：{', '.join(tools_used)}")
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description='Web Hybrid Search - 混合网络搜索',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -q "OpenAI GPT-5.4"
  %(prog)s -q "AI Agents" --limit 10
  %(prog)s -q "news" -o results.json
        """
    )
    parser.add_argument('--query', '-q', required=True, help='搜索关键词')
    parser.add_argument('--limit', '-l', type=int, default=5, help='每个工具的最大结果数')
    parser.add_argument('--min-results', type=int, default=5, help='最小结果数阈值')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示调试信息')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 执行搜索
    results = hybrid_search(
        query=args.query,
        limit=args.limit,
        min_results=args.min_results
    )
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"结果已保存到：{args.output}")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
