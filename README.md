# link-article-writer

> 从任意链接，一键生成结构清晰、有深度、配图精美的完整文章。

## 简介

link-article-writer 是一个 Claude Code Skill，能够自动解析链接并生成完整的文章。支持 YouTube 视频、知乎文章、微信公众号文章的自动解析、深度研究、文章写作、排版及配图生成。

## 核心功能

- **多平台支持**：YouTube、知乎、微信公众号
- **智能解析**：自动识别平台类型，提取标题、正文、作者、发布时间等信息
- **深度研究**：基于原文内容进行多维度扩展研究，交叉验证事实
- **专业写作**：继承 auto-writing 风格，说人话、有温度、有洞察、有节制
- **精美配图**：KAFKA 统一插画风格，极简手绘线条风

## 支持的链接类型

| 平台 | URL 格式 | 提取内容 |
|------|----------|----------|
| YouTube | `youtube.com/watch?v=...` / `youtu.be/...` | 视频元数据、字幕 |
| 知乎 | `zhihu.com/question/...` / `zhihu.com/p/...` | 问题/文章全文 |
| 微信公众号 | `mp.weixin.qq.com/...` / `weixin.qq.com/r/...` | 文章全文 |

## 工作流程

```
用户输入链接 → URL解析路由 → 内容提取 → 深度研究 → 大纲确认 → 文章写作 → 排版优化 → 配图生成 → 最终输出
```

## 安装方式

### 方式一：npx 一次性安装（推荐）

```bash
npx link-article-writer
```

### 方式二：npm 全局安装

```bash
npm install -g link-article-writer
```

### 方式三：从 GitHub 直接安装

```bash
npx github:zhuyidian/link-article-writer
```

### 安装后验证

安装完成后，技能会被部署到以下位置：
- 技能代码：`~/.agents/skills/link-article-writer/`
- 符号链接：`~/.claude/skills/link-article-writer`

---

## 快速开始

### 1. 配置 API Key

在 `config.env` 文件中配置 MiniMax API Key：

```env
MINIMAX_API_KEY=your_minimax_api_key_here
```

### 2. 使用 Skill

在 Claude Code 中使用 `/link-article-writer` 命令，然后粘贴你想要转换的链接。

### 3. 等待生成

系统会自动完成以下步骤：
- URL 解析与平台识别
- 内容提取
- 深度研究与扩展
- 生成大纲供确认
- 文章写作与自我 Review
- 排版优化
- 配图生成

---

## 版本迭代

### V1.1.0 (2026-04-03)

**新增 npm 安装支持**

- 添加 `package.json`，支持 `npx` / `npm` 全局安装
- 添加 `bin/install.js` 安装脚本，自动创建符号链接到 `~/.claude/skills/`
- 支持 `npx link-article-writer` 一键安装
- 支持 `npm install -g link-article-writer` 全局安装
- 支持 `npx github:zhuyidian/link-article-writer` 从 GitHub 直接安装

### V1.0.0 (2026-03-23)

**初始版本**

- 实现 YouTube 视频链接解析与内容提取
- 实现知乎问题/文章链接解析与内容提取
- 实现微信公众号文章链接解析与内容提取
- 实现基于 MiniMax-M2.7 的文章生成
- 实现基于 MiniMax 图像模型的配图生成
- 实现 7维度自我 Review 机制
- 实现前端进度实时同步
- 实现 KAFKA 插画风格规范

### [Future] V1.1.0

- [ ] 支持更多平台（微博、B 站、小红书等）
- [ ] 支持用户自定义文章类型和风格
- [ ] 优化深度研究模块，增加更多数据源

### [Future] V1.2.0

- [ ] 支持多语言内容翻译与生成
- [ ] 增加文章SEO优化建议
- [ ] 支持导出更多格式（HTML、PDF、Word）

### [Future] V2.0.0

- [ ] 支持自定义配图风格
- [ ] 增加团队协作功能
- [ ] 支持文章版本管理与对比

---

## 项目结构

```
link-article-writer/
├── SKILL.md                          # Skill 定义文件
├── README.md                          # 项目说明文档
├── package.json                       # npm 包配置（支持 npx 安装）
├── bin/
│   └── install.js                     # 安装脚本
├── config.env                         # 配置文件
├── scripts/
│   ├── url_parser.py                  # URL 解析与平台路由
│   ├── youtube_extractor.py           # YouTube 内容提取
│   ├── zhihu_extractor.py             # 知乎内容提取
│   ├── wechat_extractor.py            # 公众号内容提取
│   ├── minimax_caller.py              # MiniMax 文本生成
│   ├── minimax_image_generator.py     # MiniMax 图像生成
│   └── content_pipeline.py            # 内容处理管道
├── tools/
│   ├── progress_updater.py            # 前端进度同步
│   ├── prompt_generator.py            # Prompt 生成
│   └── layout_engine.py               # 图文排版
├── references/
│   ├── platform_extraction.md         # 各平台提取详细方案
│   ├── article_templates.md           # 文章类型模板
│   └── writing_prompts.md             # 写作 Prompt 模板
└── .claude/
    └── skills/
        └── link-article-writer/       # Skill 目录
```

---

## 技术栈

- **文本生成**：MiniMax-M2.7
- **图像生成**：MiniMax 图像模型
- **深度研究**：WebSearch
- **内容提取**：yt-dlp、知乎API、微信公众号爬取

---

## 写作风格

继承 auto-writing 的核心理念：

- **说人话** — 奶奶能听懂
- **有温度** — 真实的人在分享
- **有洞察** — 不只"是什么"，更要"为什么"
- **有节制** — 金句在恰当时刻闪光

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## License

MIT
