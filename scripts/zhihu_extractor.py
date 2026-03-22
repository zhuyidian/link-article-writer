#!/usr/bin/env python3
"""
Zhihu Content Extractor - Link Article Writer
提取知乎问题/文章的完整内容
"""

import json
import sys
import re
import requests
from typing import Optional

# 知乎API端点
ZHIHU_API_BASE = 'https://www.zhihu.com/api/v4'

def extract_question(question_id: str) -> dict:
    """提取知乎问题内容"""
    # 获取问题详情
    question_url = f'{ZHIHU_API_BASE}/questions/{question_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    try:
        resp = requests.get(question_url, headers=headers, timeout=10)
        resp.raise_for_status()
        question_data = resp.json()

        # 获取回答列表
        answers_url = f'{ZHIHU_API_BASE}/questions/{question_id}/answers'
        params = {
            'sort_by': 'votes',  # 按赞同数排序
            'limit': 10,
            'offset': 0,
        }

        answers_resp = requests.get(answers_url, headers=headers, params=params, timeout=10)
        answers_data = answers_resp.json()

        # 提取高赞回答内容
        answers = []
        for answer in answers_data.get('data', []):
            answers.append({
                'author': answer.get('author', {}).get('name', '匿名'),
                'content': clean_html(answer.get('content', '')),
                'votes': answer.get('voteup_count', 0),
            })

        return {
            'type': 'question',
            'title': question_data.get('title', ''),
            'detail': clean_html(question_data.get('detail', '')),
            'created': question_data.get('created', ''),
            'updated': question_data.get('updated_time', ''),
            'answers': answers,
        }

    except Exception as e:
        return {'error': str(e)}

def extract_article(article_id: str) -> dict:
    """提取知乎专栏文章"""
    article_url = f'{ZHIHU_API_BASE}/articles/{article_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    try:
        resp = requests.get(article_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return {
            'type': 'article',
            'title': data.get('title', ''),
            'content': clean_html(data.get('content', '')),
            'author': data.get('author', {}).get('name', ''),
            'created': data.get('created', ''),
            'updated': data.get('updated', ''),
            'voteup': data.get('voteup_count', 0),
            'favorites': data.get('favorited_count', 0),
        }

    except Exception as e:
        return {'error': str(e)}

def extract_column(column_slug: str) -> dict:
    """提取知乎专栏信息"""
    column_url = f'{ZHIHU_API_BASE}/columns/{column_slug}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    try:
        resp = requests.get(column_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return {
            'type': 'column',
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'followers': data.get('followers', 0),
            'articles_count': data.get('articles_count', 0),
        }

    except Exception as e:
        return {'error': str(e)}

def clean_html(html_content: str) -> str:
    """清理HTML标签，提取纯文本"""
    if not html_content:
        return ''

    # 移除script和style标签
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)

    # 处理图片
    html_content = re.sub(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>', '[图片]', html_content)

    # 处理代码块
    html_content = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'\n```\n\1\n```\n', html_content, flags=re.DOTALL)

    # 移除所有HTML标签
    text = re.sub(r'<[^>]+>', '', html_content)

    # 处理HTML实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')

    # 清理多余空白
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text

def extract(zh_type: str, content_id: str) -> dict:
    """
    主提取函数
    zh_type: question | article | column
    """
    if zh_type == 'question':
        content_data = extract_question(content_id)
    elif zh_type == 'article':
        content_data = extract_article(content_id)
    elif zh_type == 'column':
        content_data = extract_column(content_id)
    else:
        return {'success': False, 'error': f'Unknown type: {zh_type}'}

    if 'error' in content_data:
        return {'success': False, 'error': content_data['error']}

    return {
        'success': True,
        'platform': 'zhihu',
        'content_id': content_id,
        'type': zh_type,
        'data': content_data,
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python zhihu_extractor.py <question|article|column> <id>")
        sys.exit(1)

    zh_type = sys.argv[1]
    content_id = sys.argv[2]

    result = extract(zh_type, content_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
