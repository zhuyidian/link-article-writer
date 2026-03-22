# 平台内容提取详细方案

## 目录

1. [YouTube提取方案](#youtube提取方案)
2. [知乎提取方案](#知乎提取方案)
3. [微信公众号提取方案](#微信公众号提取方案)
4. [Research Report模板](#research-report模板)

---

## YouTube提取方案

### 提取优先级

| 优先级 | 方式 | 适用场景 | 质量 |
|--------|------|----------|------|
| 1 | YouTube Transcript API | 有字幕视频 | 高 |
| 2 | yt-dlp自动字幕 | 无字幕但有自动字幕 | 中 |
| 3 | Whisper语音转录 | 无字幕视频 | 取决于音频质量 |
| 4 | 视频描述+评论 | 万不得已 | 低 |

### 依赖安装

```bash
pip install yt-dlp youtube-transcript-api
```

### 字幕语言优先级

```
zh-Hans → zh-CN → zh-Hant → zh → en
```

### 输出格式

```json
{
  "platform": "youtube",
  "content_id": "dQw4w9WgXcQ",
  "metadata": {
    "title": "视频标题",
    "description": "视频描述",
    "duration": 213,
    "uploader": "上传者名称",
    "upload_date": "20240101",
    "view_count": 1000000,
    "like_count": 50000,
    "tags": ["标签1", "标签2"]
  },
  "content": "提取的字幕或描述文本...",
  "content_source": "transcript|description",
  "content_length": 5000
}
```

### 特殊情况处理

- **直播视频**：无字幕，使用视频描述+实时评论
- **音乐视频**：提取歌曲名称/艺术家/歌词（版权限制可能失败）
- **合集视频**：只提取单个视频内容，不处理整个播放列表

---

## 知乎提取方案

### 知乎内容类型

| 类型 | URL格式 | 提取重点 |
|------|---------|----------|
| 问题 | zhihu.com/question/123456 | 问题描述 + 高赞回答 |
| 文章 | zhihu.com/p/12345678 | 完整文章内容 |
| 专栏 | zhihu.com/column/xxx | 专栏信息 |

### API请求限制

- 请求频率：每分钟60次
- 需要User-Agent头
- 部分内容需要登录态

### 问题提取策略

1. 获取问题详情（标题、描述、关注者）
2. 获取Top 10高赞回答
3. 合并回答内容（按赞同数排序）

### 输出格式

```json
{
  "platform": "zhihu",
  "type": "question|article",
  "content_id": "123456",
  "data": {
    "title": "问题标题/文章标题",
    "detail": "问题补充描述/文章正文",
    "author": "作者名称",
    "created": "创建时间戳",
    "answers": [
      {
        "author": "回答者",
        "content": "回答正文（纯文本）",
        "votes": 赞同数
      }
    ]
  }
}
```

### 备选方案

如API失败，使用页面爬取：
```python
# 使用requests-html或playwright渲染
from requests_html import HTMLSession
session = HTMLSession()
r = session.get(url)
content = r.html.find('#js_content', first=True)
```

---

## 微信公众号提取方案

### 提取挑战

微信文章是主要难点：
1. 短链接需先解析
2. 部分文章需微信登录态
3. 图片可能有防盗链

### 短链接解析

```python
# weixin.qq.com/r/xxx 格式
import requests
resp = requests.head(url, allow_redirects=True)
full_url = resp.url
```

### 正文提取

```python
# 关键元素ID
# 标题: id="activity-name"
# 作者: id="js_name"
# 时间: id="publish_time"
# 正文: id="js_content"
# 封面: class="rich_pages"
```

### 图片处理

微信图片URL格式转换：
```python
# 来源格式 (可能被防盗链)
http://mmbiz.qpic.cn/xxx

# 转换后格式 (可直接访问)
https://mmbiz.qlogo.cn/mmbiz_png/xxx
```

### 登录态处理

如遇限制，备选方案：
1. 使用微信公众号爬取MCP服务
2. 记录链接，让用户手动复制内容
3. 使用替代来源（如知乎/CSDN转载）

### 输出格式

```json
{
  "platform": "wechat",
  "content_id": "abc123",
  "data": {
    "title": "文章标题",
    "author": "公众号名称",
    "publish_time": "2024-01-01",
    "content": "文章正文（纯文本）",
    "cover_image": "封面图URL",
    "images": ["图1 URL", "图2 URL"]
  }
}
```

---

## Research Report模板

解析完内容后，生成研究报告：

```markdown
# 研究报告

## 内容概览

| 项目 | 内容 |
|------|------|
| 来源平台 | YouTube/知乎/微信公众号 |
| 原文标题 | xxx |
| 原文作者 | xxx |
| 内容长度 | xxx字 |
| 内容类型 | xxx |

## 核心主题

[从原文中提取的3-5个核心主题/关键词]

## 关键观点

### 观点1
[原文的核心论点，用自己的话复述]

### 观点2
...

## 信息源质量评估

| 指标 | 评分 | 说明 |
|------|------|------|
| 可信度 | ★★★★☆ | 来源权威 |
| 时效性 | ★★★★★ | 2024年最新 |
| 完整度 | ★★★★☆ | 内容充实 |

## 补充研究方向

基于原文主题，建议补充研究：
1. [补充方向1]
2. [补充方向2]
3. [补充方向3]

## 原文链接
[原始链接]
```

---

## 依赖清单

```txt
# requirements.txt
requests>=2.28.0
yt-dlp>=2023.10.0
youtube-transcript-api>=0.6.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
```
