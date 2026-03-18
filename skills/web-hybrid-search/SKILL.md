---
name: web-hybrid-search
description: 混合网络搜索技能，整合 SearchCans、Linkup 和 web_search 三个检索工具。按照优先级策略调用多个工具，自动去重和整合结果。当用户需要全面、高质量的网络搜索结果时使用。
---

# Web Hybrid Search（混合网络搜索）

## 概述

本技能整合三个检索工具，提供全面的网络搜索能力：

1. **SearchCans** - 优先使用，擅长检索和 URL 发现
2. **Linkup** - 第二优先级，支持深度搜索和抓取
3. **web_search** - 备选方案，基础搜索能力

## 调用策略

```
┌─────────────────────────────────────┐
│         用户搜索请求                 │
└──────────────┬──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  1. SearchCans       │ ← 优先
    │  (检索 + URL 发现)     │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  2. Linkup           │ ← 如果 SearchCans 结果不足
    │  (深度搜索/抓取)      │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  3. web_search       │ ← 如果前两者结果不足
    │  (基础搜索)          │
    └──────────────────────┘
```

### 优先级规则

1. **优先使用 SearchCans**
   - 擅长发现可用 URL
   - 轻量级检索

2. **完成 SearchCans 后，选择 Linkup 或 web_search**
   - 优先使用 Linkup（功能更强）
   - 如果 Linkup 不可用，使用 web_search

3. **智能补充**
   - 如果前两个工具提供了丰富结果（≥5 条），不再调用第三个
   - 如果结果不足，使用第三个工具补充

## 使用方法

### 基础调用

```bash
python scripts/hybrid_search.py --query "OpenAI GPT-5.4"
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--query` | 搜索关键词 | 必填 |
| `--limit` | 每个工具的最大结果数 | 5 |
| `--min-results` | 最小结果数阈值 | 5 |
| `--output` | 输出文件路径 | results.json |
| `--verbose` | 显示调试信息 | 否 |

### 示例

```bash
# 基础搜索
python scripts/hybrid_search.py -q "AI Agents"

# 指定结果数量
python scripts/hybrid_search.py -q "OpenAI news" --limit 10

# 输出到文件
python scripts/hybrid_search.py -q "GPT-5.4" -o openai_results.json
```

## 结果整合

### 去重策略

1. **URL 去重** - 相同 URL 只保留一份
2. **标题去重** - 相似标题（>90% 匹配）只保留一份
3. **优先级** - 保留来自更高优先级工具的结果

### 输出顺序

按照以下优先级排序：
1. Linkup 结果
2. web_search 结果
3. SearchCans 结果

### 输出格式

```json
{
  "query": "搜索关键词",
  "timestamp": "2026-03-18T17:00:00Z",
  "tools_used": ["searchcans", "linkup"],
  "total_results": 10,
  "results": [
    {
      "source": "linkup",
      "title": "结果标题",
      "url": "https://...",
      "content": "内容摘要",
      "favicon": "https://..."
    }
  ]
}
```

## 前置要求

- `SEARCHCANS_API_KEY` - SearchCans API Key
- `LINKUP_API_KEY` - Linkup API Key
- 网络连接

## 错误处理

- 单个工具失败不影响其他工具
- 至少一个工具成功即可返回结果
- 详细记录每个工具的执行状态

## 相关资源

- SearchCans 文档：见 `../searchcans-web/SKILL.md`
- Linkup 文档：见 `../linkup-search-1.0.0/SKILL.md`
- web_search：OpenClaw 内置技能
