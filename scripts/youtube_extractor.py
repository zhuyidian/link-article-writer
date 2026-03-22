#!/usr/bin/env python3
"""
YouTube Content Extractor - Link Article Writer
提取YouTube视频内容：元数据、字幕/转录
"""

import json
import sys
import subprocess
import re
from typing import Optional

def get_video_metadata(video_id: str) -> dict:
    """使用yt-dlp获取视频元数据"""
    cmd = [
        'yt-dlp',
        '--dump-json',
        '--no-download',
        '--no-playlist',
        f'https://www.youtube.com/watch?v={video_id}'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {'error': result.stderr}

        data = json.loads(result.stdout)
        return {
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'duration': data.get('duration', 0),
            'uploader': data.get('uploader', ''),
            'upload_date': data.get('upload_date', ''),
            'view_count': data.get('view_count', 0),
            'like_count': data.get('like_count', 0),
            'tags': data.get('tags', []),
            'thumbnail': data.get('thumbnail', ''),
        }
    except Exception as e:
        return {'error': str(e)}

def get_subtitles(video_id: str, languages: list = None) -> dict:
    """获取字幕内容"""
    if languages is None:
        languages = ['zh-Hans', 'zh-CN', 'zh-Hant', 'zh', 'en']

    subtitles = {}

    # 尝试获取自动生成字幕
    for lang in languages:
        cmd = [
            'yt-dlp',
            '--write-auto-subs',
            '--skip-download',
            '--no-playlist',
            f'--sub-lang={lang}',
            '-o', '/dev/null',
            f'https://www.youtube.com/watch?v={video_id}'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            # yt-dlp 会输出字幕文件路径
            if result.returncode == 0:
                # 从stderr获取字幕文件路径
                output = result.stderr
                # 解析字幕文件路径...
                pass
        except Exception:
            continue

    return subtitles

def get_transcript(video_id: str, languages: list = None) -> Optional[str]:
    """
    获取视频转录文本
    优先使用YouTube Transcript API，失败则使用字幕下载
    """
    if languages is None:
        languages = ['zh', 'en']

    # 方法1: 尝试使用 youtube-transcript-api
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        for lang in languages:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=[lang]
                )
                # 合并成纯文本
                text = ' '.join([item['text'] for item in transcript])
                return text
            except Exception:
                continue
    except ImportError:
        pass

    # 方法2: 降级处理 - 仅返回元数据和描述
    return None

def extract(video_id: str) -> dict:
    """
    主提取函数
    返回视频的完整信息
    """
    # 获取元数据
    metadata = get_video_metadata(video_id)

    if 'error' in metadata:
        return {
            'success': False,
            'error': metadata['error']
        }

    # 获取转录
    transcript = get_transcript(video_id)

    # 组装结果
    result = {
        'success': True,
        'platform': 'youtube',
        'content_id': video_id,
        'metadata': metadata,
        'transcript': transcript,
        'content_length': len(transcript) if transcript else len(metadata.get('description', '')),
        'source': 'transcript' if transcript else 'description'
    }

    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python youtube_extractor.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    result = extract(video_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
