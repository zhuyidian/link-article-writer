#!/usr/bin/env python3
"""
WeChat Content Extractor - Link Article Writer
提取微信公众号文章的完整内容
"""

import json
import sys
import re
import requests
from typing import Optional

def resolve_short_url(short_url: str) -> str:
    """解析微信短链接为完整URL"""
    try:
        resp = requests.head(short_url, allow_redirects=True, timeout=10)
        return resp.url
    except Exception as e:
        print(f"Warning: Failed to resolve short URL: {e}", file=sys.stderr)
        return short_url

def extract_article_content(url: str) -> dict:
    """
    提取微信公众号文章内容
    注意：微信文章需要特殊处理，可能需要登录态
    备选方案：使用公众号爬取MCP或浏览器渲染
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        html = resp.text

        # 提取文章标题
        title_match = re.search(r'<h1[^>]*id="activity-name"[^>]*>([^<]+)</h1>', html)
        title = title_match.group(1).strip() if title_match else ''

        # 提取作者
        author_match = re.search(r'<a[^>]*id="js_name"[^>]*>([^<]+)</a>', html)
        author = author_match.group(1).strip() if author_match else ''

        # 提取发布时间
        time_match = re.search(r'<em[^>]*id="publish_time"[^>]*>([^<]+)</em>', html)
        publish_time = time_match.group(1).strip() if time_match else ''

        # 提取正文内容
        content_match = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>', html, re.DOTALL)
        content_html = content_match.group(1) if content_match else ''

        # 清理HTML并处理特殊元素
        content_text = clean_wechat_html(content_html)

        # 提取封面图片
        cover_match = re.search(r'<img[^>]*data-src=["\']([^"\']*?)["\'][^>]*class="rich_pages[^"]*"', html)
        cover_image = cover_match.group(1) if cover_match else ''

        return {
            'title': title,
            'author': author,
            'publish_time': publish_time,
            'content': content_text,
            'cover_image': cover_image,
            'url': url,
        }

    except Exception as e:
        return {'error': str(e)}

def clean_wechat_html(html_content: str) -> str:
    """清理微信公众号HTML"""
    if not html_content:
        return ''

    # 移除script和style
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)

    # 处理图片 - 微信图片格式转换
    html_content = re.sub(r'<img[^>]*data-src=["\']([^"\']*)["\'][^>]*>', r'\n[图片: \1]\n', html_content)
    html_content = re.sub(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>', r'\n[图片: \1]\n', html_content)

    # 处理section标签（微信的section）
    html_content = re.sub(r'<section[^>]*>', '', html_content)
    html_content = re.sub(r'</section>', '', html_content)

    # 处理代码块
    html_content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html_content, flags=re.DOTALL)

    # 移除所有HTML标签
    text = re.sub(r'<[^>]+>', '', html_content)

    # 处理HTML实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&apos;', "'")

    # 清理多余空白
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text

def extract(url: str) -> dict:
    """
    主提取函数
    """
    # 如果是短链接，先解析
    if 'weixin.qq.com/r/' in url:
        url = resolve_short_url(url)

    content_data = extract_article_content(url)

    if 'error' in content_data:
        return {
            'success': False,
            'error': content_data['error'],
            'platform': 'wechat'
        }

    return {
        'success': True,
        'platform': 'wechat',
        'url': url,
        'data': content_data,
        'content_length': len(content_data.get('content', ''))
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python wechat_extractor.py <wechat_article_url>")
        sys.exit(1)

    url = sys.argv[1]
    result = extract(url)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
