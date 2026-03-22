#!/usr/bin/env python3
"""
MiniMax API Caller - Link Article Writer
使用 MiniMax-M2.7 模型进行文本生成
"""

import os
import json
import sys
import requests
from typing import Optional, Dict, List
from pathlib import Path

class MiniMaxCaller:
    """MiniMax API 调用器"""

    BASE_URL = "https://api.minimax.chat/v1"

    def __init__(self, api_key: str = None, model: str = "MiniMax-Text-01"):
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY", "")
        self.model = model

        if not self.api_key:
            print("警告: MINIMAX_API_KEY 未配置")

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

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Optional[str]:
        """
        发送对话请求

        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "xxx"}]
            temperature: 温度参数
            max_tokens: 最大Token数

        Returns:
            生成的文本，失败返回 None
        """
        if not self.api_key:
            config = self._load_config()
            self.api_key = config.get("MINIMAX_API_KEY", "")

        if not self.api_key:
            print("错误: MINIMAX_API_KEY 未配置")
            return None

        url = f"{self.BASE_URL}/text/chatcompletion_v2"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)
            response.raise_for_status()

            result = response.json()
            choices = result.get("choices", [])

            if choices:
                return choices[0].get("message", {}).get("content", "")

            return None

        except requests.exceptions.Timeout:
            print("请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
        except Exception as e:
            print(f"生成失败: {e}")
            return None

    def generate(
        self,
        prompt: str,
        system_prompt: str = "你是一个专业的内容创作助手。",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Optional[str]:
        """
        简化调用：直接传入 prompt 获取生成结果

        Args:
            prompt: 用户输入
            system_prompt: 系统提示
            temperature: 温度
            max_tokens: 最大Token数

        Returns:
            生成的文本
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        return self.chat(messages, temperature, max_tokens)


def main():
    """测试"""
    if len(sys.argv) < 2:
        print("Usage: python minimax_caller.py <prompt>")
        sys.exit(1)

    prompt = sys.argv[1]
    caller = MiniMaxCaller()

    print("调用 MiniMax-M2.7...")
    result = caller.generate(prompt)

    if result:
        print("\n=== 生成结果 ===")
        print(result)
    else:
        print("生成失败")


if __name__ == "__main__":
    main()
