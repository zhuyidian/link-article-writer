#!/usr/bin/env python3
"""
MiniMax Image Generator - Link Article Writer
使用 MiniMax API 生成图片
"""

import os
import json
import time
import asyncio
import base64
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class GenerationResult:
    """生成结果"""
    id: str
    status: str  # success / failed / pending
    path: Optional[str] = None
    position: str = ""
    error: Optional[str] = None

@dataclass
class BatchResult:
    """批量生成结果"""
    total: int
    success: int
    failed: int
    results: List[GenerationResult]

class MiniMaxImageGenerator:
    """MiniMax 图像生成器"""

    BASE_URL = "https://api.minimax.chat/v1"

    def __init__(self, api_key: str = None, model: str = "image-01"):
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY", "")
        self.model = model

        # 代理配置
        self.http_proxy = os.environ.get("HTTP_PROXY", "")
        self.https_proxy = os.environ.get("HTTPS_PROXY", "")

        self.proxies = {}
        if self.http_proxy:
            self.proxies['http'] = self.http_proxy
        if self.https_proxy:
            self.proxies['https'] = self.https_proxy

        if not self.api_key:
            print("警告: MINIMAX_API_KEY 未配置")
        else:
            print(f"已配置 MiniMax API，模型: {self.model}")

    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = Path(__file__).parent.parent.parent.parent / "config.env"
        config = {}

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip().strip('"\'')

        return config

    def generate_single(
        self,
        prompt: str,
        negative_prompt: str = "",
        output_path: str = None,
        width: int = 1024,
        height: int = 576
    ) -> Optional[str]:
        """
        生成单张图片

        Args:
            prompt: 正向提示词
            negative_prompt: 负向提示词
            output_path: 输出路径
            width: 图片宽度
            height: 图片高度

        Returns:
            生成的图片路径，失败返回 None
        """
        if not self.api_key:
            config = self._load_config()
            self.api_key = config.get("MINIMAX_API_KEY", "")

        if not self.api_key:
            print("API Key 未配置")
            return None

        url = f"{self.BASE_URL}/image_generation"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # MiniMax 图像生成请求格式
        data = {
            "model": self.model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_images": 1,
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=120,
                proxies=self.proxies if self.proxies else None
            )

            if response.status_code != 200:
                print(f"API 错误 ({response.status_code}): {response.text[:500]}")
                return None

            result = response.json()

            # 提取图片数据
            if "data" in result and len(result["data"]) > 0:
                image_info = result["data"][0]
                image_url = image_info.get("url", "")

                if image_url and output_path:
                    # 下载图片
                    img_response = requests.get(
                        image_url,
                        timeout=60,
                        proxies=self.proxies if self.proxies else None
                    )
                    img_response.raise_for_status()

                    # 确保目录存在
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    # 保存图片
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)

                    return str(output_path)

                # 也可能是 base64 格式
                if "base64" in image_info:
                    image_bytes = base64.b64decode(image_info["base64"])

                    if output_path:
                        output_path = Path(output_path)
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(output_path, 'wb') as f:
                            f.write(image_bytes)

                    return str(output_path)

            print("响应中未找到图片数据")
            return None

        except requests.exceptions.Timeout:
            print("请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
        except Exception as e:
            print(f"生成图片失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def generate_batch_async(
        self,
        prompts: List[Dict],
        output_dir: str,
        delay: float = 2.0
    ) -> BatchResult:
        """
        异步批量生成图片

        Args:
            prompts: Prompt 列表
            output_dir: 输出目录
            delay: 请求间隔（秒）

        Returns:
            批量生成结果
        """
        os.makedirs(output_dir, exist_ok=True)
        results = []

        for prompt_data in prompts:
            prompt_id = prompt_data.get('id', 'img')
            prompt_text = prompt_data.get('prompt', '')
            negative = prompt_data.get('negative_prompt', '')
            position = prompt_data.get('position', '')

            output_path = os.path.join(output_dir, f"{prompt_id}.png")

            print(f"\n生成 {prompt_id}...")
            print(f"  Prompt: {prompt_text[:100]}...")

            try:
                result_path = self.generate_single(
                    prompt=prompt_text,
                    negative_prompt=negative,
                    output_path=output_path
                )

                if result_path and os.path.exists(result_path):
                    results.append(GenerationResult(
                        id=prompt_id,
                        status='success',
                        path=result_path,
                        position=position
                    ))
                    print(f"  成功: {result_path}")
                else:
                    results.append(GenerationResult(
                        id=prompt_id,
                        status='failed',
                        position=position,
                        error='生成失败或文件未保存'
                    ))
                    print(f"  失败")

            except Exception as e:
                results.append(GenerationResult(
                    id=prompt_id,
                    status='failed',
                    position=position,
                    error=str(e)
                ))
                print(f"  错误: {e}")

            # 请求间隔，避免 rate limit
            if delay > 0:
                await asyncio.sleep(delay)

        success_count = len([r for r in results if r.status == 'success'])
        failed_count = len([r for r in results if r.status == 'failed'])

        return BatchResult(
            total=len(prompts),
            success=success_count,
            failed=failed_count,
            results=results
        )

    def generate_batch(
        self,
        prompts: List[Dict],
        output_dir: str,
        delay: float = 2.0
    ) -> BatchResult:
        """同步版本的批量生成"""
        return asyncio.run(self.generate_batch_async(prompts, output_dir, delay))


class MockImageGenerator:
    """模拟图像生成器（用于测试）"""

    def __init__(self):
        pass

    def generate_batch(
        self,
        prompts: List[Dict],
        output_dir: str,
        delay: float = 0.1
    ) -> BatchResult:
        """批量生成模拟图片"""
        os.makedirs(output_dir, exist_ok=True)
        results = []

        for prompt_data in prompts:
            prompt_id = prompt_data.get('id', 'img')
            position = prompt_data.get('position', '')
            prompt_type = prompt_data.get('type', 'image')

            output_path = os.path.join(output_dir, f"{prompt_id}.png")

            try:
                from PIL import Image, ImageDraw

                width, height = 1024, 576
                img = Image.new('RGB', (width, height))

                # 简单渐变背景
                for y in range(height):
                    r = int(200 + 40 * (y / height))
                    g = int(210 + 30 * (y / height))
                    b = int(230 + 20 * (y / height))
                    for x in range(width):
                        img.putpixel((x, y), (r, g, b))

                draw = ImageDraw.Draw(img)
                text = f"[{prompt_type.upper()}]\n{prompt_id}"
                draw.text((width//2, height//2), text, fill=(100, 100, 120), anchor='mm')

                img.save(output_path)

                results.append(GenerationResult(
                    id=prompt_id,
                    status='success',
                    path=output_path,
                    position=position
                ))
                print(f"  Mock 生成: {output_path}")

            except ImportError:
                with open(output_path.replace('.png', '.txt'), 'w') as f:
                    f.write(f"Placeholder for {prompt_id}\n{prompt_data.get('prompt', '')}")

                results.append(GenerationResult(
                    id=prompt_id,
                    status='success',
                    path=output_path.replace('.png', '.txt'),
                    position=position
                ))

            time.sleep(delay)

        return BatchResult(
            total=len(prompts),
            success=len(results),
            failed=0,
            results=results
        )


# 便捷函数
def generate_images(
    prompts: List[Dict],
    output_dir: str,
    config_path: str = None,
    use_mock: bool = False
) -> Dict:
    """
    生成图片（便捷函数）

    Args:
        prompts: Prompt 列表
        output_dir: 输出目录
        config_path: 配置文件路径
        use_mock: 是否使用模拟生成器

    Returns:
        生成结果
    """
    if use_mock:
        generator = MockImageGenerator()
    else:
        generator = MiniMaxImageGenerator()

    result = generator.generate_batch(prompts, output_dir)

    return {
        'total': result.total,
        'success': result.success,
        'failed': result.failed,
        'results': [asdict(r) for r in result.results]
    }


if __name__ == "__main__":
    # 测试
    test_prompts = [
        {
            'id': 'img_001',
            'type': 'hero',
            'prompt': 'Minimalist hand-drawn illustration of AI assistant helping human, sketch style with warm cream background',
            'negative_prompt': 'ugly, blurry, text, words, gradient',
            'position': 'before_paragraph_1'
        }
    ]

    print("=== 测试图像生成 (MiniMax) ===\n")

    print("真实 API 测试:")
    result = generate_images(
        prompts=test_prompts,
        output_dir='./test_images_minimax',
        use_mock=False
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
