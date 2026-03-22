#!/usr/bin/env python3
"""
URL Parser - Link Article Writer
统一解析YouTube、知乎、微信公众号链接
"""

import re
import json
import sys
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedURL:
    platform: str  # youtube | zhihu | wechat
    content_id: str
    original_url: str
    resolved_url: str
    metadata: dict

def extract_youtube_id(url: str) -> Optional[str]:
    """从YouTube URL提取视频ID"""
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_zhihu_id(url: str) -> tuple:
    """从知乎URL提取类型和ID"""
    # 知乎问题链接
    question_match = re.search(r'zhihu\.com/question/(\d+)', url)
    if question_match:
        return ('question', question_match.group(1))

    # 知乎文章链接
    article_match = re.search(r'zhihu\.com/p/(\d+)', url)
    if article_match:
        return ('article', article_match.group(1))

    # 知乎专栏
    column_match = re.search(r'zhihu\.com/column/([a-zA-Z0-9_-]+)', url)
    if column_match:
        return ('column', column_match.group(1))

    return (None, None)

def resolve_wechat_short_url(url: str) -> str:
    """解析微信短链接"""
    # 微信短链接格式: weixin.qq.com/r/xxx
    # 需要通过HTTP请求获取重定向后的完整URL
    import urllib.request
    import urllib.error

    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.url
    except Exception as e:
        print(f"Warning: Failed to resolve short URL: {e}", file=sys.stderr)
        return url

def extract_wechat_article_id(url: str) -> Optional[str]:
    """从微信公众号文章URL提取文章ID"""
    # mp.weixin.qq.com/s/xxx 格式
    match = re.search(r'mp\.weixin\.qq\.com/s/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)

    # 完整文章链接格式
    match = re.search(r'mp\.weixin\.qq\.com/s\?([^&]+)', url)
    if match:
        return match.group(1)

    return None

def parse_url(url: str) -> ParsedURL:
    """
    主解析函数
    返回统一格式的解析结果
    """
    url = url.strip()

    # YouTube
    if 'youtube.com' in url or 'youtu.be' in url:
        video_id = extract_youtube_id(url)
        if video_id:
            return ParsedURL(
                platform='youtube',
                content_id=video_id,
                original_url=url,
                resolved_url=f'https://www.youtube.com/watch?v={video_id}',
                metadata={'video_id': video_id}
            )

    # 知乎
    elif 'zhihu.com' in url:
        zh_type, zh_id = extract_zhihu_id(url)
        if zh_id:
            resolved = f'https://www.zhihu.com/{zh_type}/{zh_id}' if zh_type != 'column' else f'https://www.zhihu.com/column/{zh_id}'
            return ParsedURL(
                platform='zhihu',
                content_id=zh_id,
                original_url=url,
                resolved_url=resolved,
                metadata={'type': zh_type, 'id': zh_id}
            )

    # 微信公众号
    elif 'weixin.qq.com' in url:
        # 短链接需要解析
        if 'weixin.qq.com/r/' in url:
            resolved = resolve_wechat_short_url(url)
        else:
            resolved = url

        article_id = extract_wechat_article_id(resolved)
        return ParsedURL(
            platform='wechat',
            content_id=article_id or 'unknown',
            original_url=url,
            resolved_url=resolved,
            metadata={'article_id': article_id}
        )

    # 未知平台
    raise ValueError(f"Unsupported URL platform: {url}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python url_parser.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    try:
        result = parse_url(url)
        print(json.dumps({
            'platform': result.platform,
            'content_id': result.content_id,
            'original_url': result.original_url,
            'resolved_url': result.resolved_url,
            'metadata': result.metadata,
            'success': True
        }, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

if __name__ == '__main__':
    main()
