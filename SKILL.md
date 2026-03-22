---
name: link-article-writer
description: |
  自动解析链接并生成完整文章的Skill。支持YouTube视频、知乎文章、微信公众号文章的自动解析、深度研究、文章写作、排版及配图生成。
  触发条件：
  - 用户提供一个YouTube/知乎/公众号链接并要求生成文章
  - 用户说"帮我写一篇关于这个链接的文章"
  - 用户请求解析某个链接内容并生成文章
  功能：URL解析 → 内容提取 → 深度调研 → 大纲生成 → 文章写作 → 排版优化 → MiniMax配图生成
---

# Link Article Writer - 链接到完整文章

> 从任意链接，一键生成结构清晰、有深度、配图精美的完整文章。

## 模型配置

| 阶段 | 模型 | 环境变量 | 配置文件 |
|------|------|----------|----------|
| **写作与内容处理** | MiniMax-M2.7 | `MINIMAX_API_KEY` | config.env |
| **配图生成** | MiniMax 图像模型 | `MINIMAX_API_KEY` | config.env |
| **深度调研** | WebSearch | 内置 | - |

**MiniMax API 配置**：
```env
# config.env
MINIMAX_API_KEY=your_minimax_api_key_here
```

调用脚本：
- 文本生成：`scripts/minimax_caller.py`
- 图像生成：`scripts/minimax_image_generator.py`

---

## 核心流程

```
用户输入链接 → URL解析路由 → 内容提取 → 深度研究 → 大纲确认 → 文章写作 → 排版优化 → 配图生成 → 最终输出
```

## 前端实时同步（强制执行）

**每个阶段必须调用 `progress_updater.py` 更新前端状态！**

工具路径：`.claude/skills/link-article-writer/tools/progress_updater.py`

### 同步命令

| 阶段 | 命令 | 示例 |
|------|------|------|
| 任务开始 | `init` | `python tools/progress_updater.py init "文章标题"` |
| URL解析完成 | `step` | `python tools/progress_updater.py step "url_parser" "YouTube链接解析完成"` |
| 内容提取完成 | `step` | `python tools/progress_updater.py step "extraction" "YouTube字幕提取完成，5000字"` |
| 研究完成 | `research` | `python tools/progress_updater.py research '{...}'` |
| 大纲完成 | `step` | `python tools/progress_updater.py step "outline" "大纲已生成，等待确认"` |
| 文章完成 | `article` | `python tools/progress_updater.py article '{...}'` |
| 配图完成 | `step` | `python tools/progress_updater.py step "images" "5张配图生成完成"` |
| 任务结束 | `complete` | `python tools/progress_updater.py complete` |

### 进度百分比参考

| 阶段 | 进度范围 |
|------|----------|
| URL解析 | 0-5% |
| 内容提取 | 5-15% |
| 深度研究 | 15-30% |
| 大纲生成 | 30-40% |
| 文章写作 | 40-70% |
| 排版优化 | 70-80% |
| 配图生成 | 80-95% |
| 最终输出 | 95-100% |

---

## 模块一：URL解析与路由

### 平台识别规则

```python
# YouTube
if "youtube.com/watch" in url or "youtu.be/" in url:
    platform = "youtube"
    video_id = extract_youtube_id(url)

# 知乎
elif "zhihu.com/question" in url:
    platform = "zhihu"
    question_id = extract_zhihu_question_id(url)
elif "zhihu.com/p/" in url:
    platform = "zhihu"
    article_id = extract_zhihu_article_id(url)

# 微信公众号
elif "weixin.qq.com/r/" in url or "mp.weixin.qq.com/" in url:
    platform = "wechat"
    article_url = resolve_wechat_url(url)  # 短链接需要解析
```

### URL解析脚本

使用 `scripts/url_parser.py` 进行标准化解析：

```bash
python scripts/url_parser.py "<用户输入的链接>"
```

输出格式：
```json
{
  "platform": "youtube|zhihu|wechat",
  "content_id": "xxx",
  "original_url": "xxx",
  "resolved_url": "xxx",
  "metadata": {}
}
```

---

## 模块二：内容提取

### YouTube 提取流程

1. 使用 `yt-dlp` 获取视频元数据（标题、描述、时长）
2. 获取字幕（优先中文，其次英文）
3. 如无字幕，使用 `whisper` 转录音频

关键脚本：`scripts/youtube_extractor.py`

### 知乎提取流程

1. 直接请求知乎API获取问题/文章内容
2. 提取标题、正文、作者、发布时间
3. 处理图片和代码块

关键脚本：`scripts/zhihu_extractor.py`

### 微信公众号提取流程

1. 短链接（如 `weixin.qq.com/r/xxx`）需先解析为完整URL
2. 使用公众号爬取工具或浏览器渲染获取正文
3. 提取标题、正文、作者、发布时间

关键脚本：`scripts/wechat_extractor.py`

详细提取方案见：[references/platform_extraction.md](references/platform_extraction.md)

---

## 模块三：深度研究

### 研究策略

| 原内容类型 | 扩展研究方向 |
|-----------|------------|
| 科技评测 | 竞品对比、用户评价、行业地位 |
| 深度分析 | 背景信息、相关事件、多方观点 |
| 教程指南 | 延伸场景、常见问题、进阶路径 |
| 热点评论 | 事件经过、各方反应、历史先例 |

### 研究执行

1. **主题提取**：从原文提取3-5个核心关键词
2. **Web搜索**：每个关键词搜索Top 5相关信息源
3. **观点交叉**：查找支持/反对的不同声音
4. **数据验证**：识别原文中的数据claim并验证

### Research Report 输出

见 [references/platform_extraction.md](references/platform_extraction.md)

---

## 模块四：大纲生成

### 文章类型与结构映射

| 文章类型 | 推荐结构 |
|---------|---------|
| 科技评测 | 开场 → 产品介绍 → 核心体验 → 优缺点 → 总结建议 |
| 深度分析 | 现象/事件 → 背景原因 → 多角度分析 → 趋势展望 |
| 教程指南 | 问题场景 → 解决方案 → 步骤讲解 → 常见坑点 → 进阶提示 |
| 热点评论 | 事件概述 → 各方反应 → 深度解读 → 个人立场 → 开放思考 |

### 大纲生成流程

1. 分析原文核心观点和结构
2. 结合用户文章类型要求（如有）
3. 生成3个差异化大纲选项
4. 展示给用户选择/确认

详细模板见：[references/article_templates.md](references/article_templates.md)

---

## 模块五：文章写作

### 写作哲学

继承 `auto-writing` 风格的核心理念：
- **说人话** — 奶奶能听懂
- **有温度** — 真实的人在分享
- **有洞察** — 不只"是什么"，更要"为什么"
- **有节制** — 金句在恰当时刻闪光

### 写作流水线

**Stage 1: 初稿生成** → 展示给用户
**Stage 2: 自我Review** → 7维度评分
**Stage 3: 终稿润色** → 用户确认

### 7维度自我Review

| 维度 | 检查项 |
|------|--------|
| 准确性 | 事实、数据、引用是否正确 |
| 逻辑性 | 论证链条是否清晰 |
| 可读性 | 语言是否流畅易懂 |
| 深度 | 是否有独特洞察 |
| 原创性 | 是否有差异化观点 |
| 结构 | 章节安排是否合理 |
| 配图契合 | 文字与配图是否匹配 |

详细Prompt见：[references/writing_prompts.md](references/writing_prompts.md)

---

## 模块六：排版优化

### 输出格式

**最终输出格式：Markdown (.md)**

### 排版规范

```markdown
# 一级标题

## 二级标题

### 三级标题

> 引用内容

**加粗内容**

[链接文字](URL)

`行内代码`

```代码块```

[插图：img_id - 描述]

---

分隔线
```

### 文章结构

- 文件名：`{主题}_{日期}.md`
- 编码：UTF-8
- 换行：LF

---

## 模块七：配图生成

### 视觉风格

继承 `auto-writing` 的统一插画风格：

```
KAFKA 插画风格规范
风格：纯手绘线条风，极简主义
线条：单色细线（深棕 #3D3D3D 或黑色 #1A1A1A）
背景：统一高端米黄色 #F5F0E6
填充：无填充或极淡的同色系晕染
文案：可有少量手写风格英文标注，不超过3个单词
禁止：渐变、阴影、3D效果、复杂纹理、多色彩
```

### 占位符规范

```
[插图：{image_id} - {描述}]
```

### Prompt生成流程

1. 理解段落主旨
2. 抽象隐喻元素
3. 描述极简画面

详细Prompt模板见 `references/writing_prompts.md`

### 生图工具

使用 `scripts/minimax_image_generator.py` 调用 MiniMax API 批量生成。

---

## 工具脚本清单

| 脚本 | 功能 | 模型 |
|------|------|------|
| `scripts/url_parser.py` | URL解析与平台路由 | - |
| `scripts/youtube_extractor.py` | YouTube内容提取 | yt-dlp |
| `scripts/zhihu_extractor.py` | 知乎内容提取 | 知乎API |
| `scripts/wechat_extractor.py` | 公众号内容提取 | requests |
| `scripts/minimax_caller.py` | MiniMax文本生成 | **MiniMax-M2.7** |
| `scripts/minimax_image_generator.py` | MiniMax批量生图 | **MiniMax** |
| `tools/progress_updater.py` | 前端进度同步 | 复用 auto-writing |
| `tools/prompt_generator.py` | Prompt生成 | 复用 auto-writing |
| `tools/layout_engine.py` | 图文排版 | 复用 auto-writing |

---

## 引用文件

- [references/platform_extraction.md](references/platform_extraction.md) - 各平台提取详细方案
- [references/article_templates.md](references/article_templates.md) - 文章类型模板
- [references/writing_prompts.md](references/writing_prompts.md) - 写作Prompt模板
