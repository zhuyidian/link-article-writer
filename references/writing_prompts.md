# 写作Prompt模板

## 目录

1. [内容理解Prompt](#内容理解prompt)
2. [大纲生成Prompt](#大纲生成prompt)
3. [文章写作Prompt](#文章写作prompt)
4. [7维度自我Review](#7维度自我review)
5. [插图Prompt模板](#插图prompt模板)

---

## 内容理解Prompt

### 提取核心主题

```
你是一个内容分析专家。请从以下原文内容中提取：

1. **核心主题**（3-5个关键词）
2. **文章类型**（科技评测/深度分析/教程指南/热点评论）
3. **目标读者**（什么样的人会读这篇文章）
4. **核心观点**（作者想要传达的主要观点，3条）
5. **信息增量**（这篇文章相比同类内容有什么新信息）

原文内容：
---
{extracted_content}
---

请用JSON格式输出：
{
  "core_topics": [...],
  "article_type": "xxx",
  "target_audience": "xxx",
  "core_points": [...],
  "new_information": [...]
}
```

### 生成Research补充方向

```
基于原文内容的主题「{core_topic}」，请提出5个补充研究方向，
帮助生成更全面的文章。每个方向请说明：
- 研究什么问题
- 预计从什么角度切入
- 推荐搜索关键词

输出格式：
1. [方向名称]
   - 问题：
   - 角度：
   - 关键词：
```

---

## 大纲生成Prompt

### 生成文章大纲

```
你是一个专业的内容策划。请为文章生成大纲。

## 基本信息
- 文章类型：{article_type}
- 核心主题：{core_topic}
- 目标字数：{word_count}字
- 目标读者：{target_audience}

## 原文核心观点
{core_points}

## 补充研究信息
{research_findings}

## 要求
1. 生成3个差异化的大纲选项
2. 每个大纲包含完整的章节结构
3. 说明每个大纲的亮点和适用场景
4. 符合{article_type}类型的结构范式

## 输出格式
### 选项A：[大纲名称]
**亮点**：xxx
**适用**：xxx

## 章节结构
1. [章节]
2. [章节]
...

---
```

---

## 文章写作Prompt

### 初稿生成

```
你是一个资深内容创作者，擅长写有深度、有洞察的文章。

## 文章信息
- 标题：{title}
- 类型：{article_type}
- 字数要求：{word_count}字
- 风格：{style_guide}

## 大纲
{outline}

## 原文内容摘要
{content_summary}

## 补充研究
{research_findings}

## 写作要求

### 核心原则
1. **说人话** — 奶奶能听懂，避免过度术语
2. **有温度** — 真实的人在分享经验
3. **有洞察** — 不只"是什么"，更要"为什么"
4. **有节制** — 金句在恰当时刻闪光

### 禁止清单
- "众所周知..." "让我们来看看..." "首先...其次...最后..."
- "这是一个革命性的技术" "简单来说..."
- 过度感叹号、堆砌术语

### 配图规划
在需要插图的位置使用占位符：
📍 [插图：img_{id} - {图片描述}]

## 开始写作
请生成完整的文章内容。
```

### 润色优化

```
你是一个资深编辑。请对以下文章进行润色优化。

## 原文章
{original_article}

## 润色要求
1. 优化开头HOOK，吸引读者
2. 改善逻辑过渡，使文章更流畅
3. 删除冗余表达，精简文字
4. 增强金句，提升可读性
5. 确保专业术语被通俗化解释

## 输出
直接输出润色后的文章，不要解释修改了什么。
```

---

## 7维度自我Review

### Review Prompt

```
你是一个严格的内容审核专家。请对以下文章进行7维度评分和审核。

## 待审核文章
{article_content}

## 评分维度

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 准确性 | 25% | 事实、数据、引用是否正确 |
| 逻辑性 | 20% | 论证链条是否清晰连贯 |
| 可读性 | 20% | 语言是否流畅易懂 |
| 深度 | 15% | 是否有独特洞察 |
| 原创性 | 10% | 是否有差异化观点 |
| 结构 | 5% | 章节安排是否合理 |
| 配图契合 | 5% | 文字与配图是否匹配 |

## 输出格式

```json
{
  "scores": {
    "accuracy": {"score": X, "max": 5, "comment": "..."},
    "logic": {"score": X, "max": 5, "comment": "..."},
    "readability": {"score": X, "max": 5, "comment": "..."},
    "depth": {"score": X, "max": 5, "comment": "..."},
    "originality": {"score": X, "max": 5, "comment": "..."},
    "structure": {"score": X, "max": 5, "comment": "..."},
    "image_match": {"score": X, "max": 5, "comment": "..."}
  },
  "overall_score": X.X,
  "strengths": [...],
  "issues": [...],
  "improvement_suggestions": [...]
}
```

### AI味检测

```
请检测以下文章中可能被认为是"AI写作"的痕迹：

检测项：
1. 过度规整的句式
2. 重复出现的连接词
3. 过于完美的结构
4. 缺乏个人风格表达

输出：
- AI味评分：X/10
- 具体问题位置和建议修改
```

---

## 插图Prompt模板

### 图片规划

```
根据以下文章内容，规划需要生成的配图：

## 文章主题
{article_topic}

## 文章大纲
{article_outline}

## 配图需求

| 图片ID | 位置 | 类型 | 描述 |
|--------|------|------|------|
| img_hero | 开头 | HERO | 头图，核心概念视觉化 |
| img_1 | Section 1 | CONCEPT | 概念解释 |
| img_2 | Section 2 | ANALOGY | 类比场景 |
| ... | | | |

### 图片类型说明
- **HERO**：头图，文章核心概念的视觉隐喻
- **CONCEPT**：概念可视化，将抽象概念具象化
- **ANALOGY**：类比场景图，配合文中类比
- **DIAGRAM**：流程/结构图，用线条连接的元素关系
- **MOOD**：氛围图，留白较多的意境图

请根据文章内容，生成详细的配图规划。
```

### Prompt生成

```
你是一个插画师Prompt专家。请为以下配图需求生成详细的Prompt。

## 配图ID
{image_id}

## 配图类型
{image_type}

## 配图位置
文章「{section_title}」章节

## 段落内容
{paragraph_content}

## 配图描述
{image_description}

## 风格要求
请生成符合KAFKA插画风格的Prompt：
- 纯手绘线条风，极简主义
- 线条：单色细线（深棕 #3D3D3D 或黑色 #1A1A1A）
- 背景：统一高端米黄色 #F5F0E6
- 填充：无填充或极淡的同色系晕染
- 文案：可有少量手写风格英文标注，不超过3个单词
- 禁止：渐变、阴影、3D效果、复杂纹理、多色彩

## 输出格式
```
[STYLE PREFIX]

SCENE DESCRIPTION:
- Main element: [核心视觉元素]
- Secondary elements: [辅助元素]
- Composition: [构图]
- Optional label: [可选标注]

NEGATIVE PROMPT:
photorealistic, 3D render, gradient, shadow, complex texture, colorful, cartoon style, anime, digital art, multiple colors, busy background
```
```

### 批量生图配置

```python
# tools/batch_image_generator.py 配置示例

IMAGES_CONFIG = {
    "aspect_ratio": "16:9",
    "style": "hand-drawn line art, minimalist",
    "output_dir": "./output/images",
    "model": "imagen-3.0",
}

PROMPT_PREFIX = """
STRICT STYLE REQUIREMENTS:
- Style: Hand-drawn line art, minimalist sketch style
- Lines: Single-weight organic lines in dark brown (#3D3D3D)
- Background: Solid warm cream color (#F5F0E6)
- Fill: No fill, or very light same-tone wash
- Text: Maximum 3 handwritten-style English words as labels
- Aesthetic: Editorial illustration style
- NO gradients, NO shadows, NO 3D effects, NO complex textures, NO multiple colors
- Aspect ratio: 16:9
"""
```
