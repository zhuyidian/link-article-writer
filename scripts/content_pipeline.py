#!/usr/bin/env python3
"""
Content Pipeline - Link Article Writer
内容处理主管道，串联各模块
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Optional

# 复用auto-writing的工具
AUTO_WRITING_TOOLS = Path(__file__).parent.parent / ".." / "auto-writing" / "tools"
LINK_WRITER_TOOLS = Path(__file__).parent.parent / "tools"
LINK_WRITER_SCRIPTS = Path(__file__).parent.parent / "scripts"

def run_url_parser(url: str) -> dict:
    """URL解析"""
    cmd = [
        sys.executable,
        str(LINK_WRITER_SCRIPTS / "url_parser.py"),
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def run_content_extraction(platform: str, content_id: str, metadata: dict) -> dict:
    """内容提取"""
    if platform == "youtube":
        cmd = [
            sys.executable,
            str(LINK_WRITER_SCRIPTS / "youtube_extractor.py"),
            content_id
        ]
    elif platform == "zhihu":
        zh_type = metadata.get("type", "question")
        cmd = [
            sys.executable,
            str(LINK_WRITER_SCRIPTS / "zhihu_extractor.py"),
            zh_type,
            content_id
        ]
    elif platform == "wechat":
        cmd = [
            sys.executable,
            str(LINK_WRITER_SCRIPTS / "wechat_extractor.py"),
            metadata.get("resolved_url", "")
        ]
    else:
        return {"success": False, "error": f"Unknown platform: {platform}"}

    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def main():
    """主管道入口"""
    if len(sys.argv) < 2:
        print("Usage: python content_pipeline.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Processing URL: {url}")

    # Step 1: URL解析
    print("\n[Step 1/4] URL解析...")
    parse_result = run_url_parser(url)
    if not parse_result.get("success"):
        print(f"URL解析失败: {parse_result.get('error')}")
        sys.exit(1)

    platform = parse_result["platform"]
    content_id = parse_result["content_id"]
    print(f"平台: {platform}, 内容ID: {content_id}")

    # Step 2: 内容提取
    print("\n[Step 2/4] 内容提取...")
    extract_result = run_content_extraction(platform, content_id, parse_result)
    if not extract_result.get("success"):
        print(f"内容提取失败: {extract_result.get('error')}")
        sys.exit(1)

    print(f"内容提取成功，长度: {extract_result.get('content_length', 0)}字")

    # Step 3: 汇总结果
    print("\n[Step 3/4] 内容分析...")
    # 这里应该调用LLM进行内容分析，生成主题、要点等
    # 简化处理，直接输出提取结果

    # Step 4: 输出
    print("\n[Step 4/4] 完成")
    output = {
        "url": url,
        "platform": platform,
        "extraction": extract_result,
        "next_steps": [
            "1. 分析提取的内容，生成核心主题和要点",
            "2. 进行深度研究，补充相关信息",
            "3. 生成文章大纲",
            "4. 写作文章",
            "5. 生成配图",
            "6. 最终输出"
        ]
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
