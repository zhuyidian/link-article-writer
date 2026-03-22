# 工具复用说明

本 Skill 复用 `auto-writing` 的工具，通过符号链接或直接调用：

## 复用工具清单

| 工具 | 来源 | 用途 |
|------|------|------|
| `progress_updater.py` | `auto-writing/tools/` | 前端进度同步 |
| `batch_image_generator.py` | `auto-writing/tools/` | Gemini批量生图 |
| `prompt_generator.py` | `auto-writing/tools/` | Prompt生成 |
| `layout_engine.py` | `auto-writing/tools/` | 图文排版 |

## 使用方式

在 SKILL.md 中已配置完整路径：

```
工具路径：.claude/skills/link-article-writer/tools/progress_updater.py
```

调用时使用 Python 执行：

```bash
python tools/progress_updater.py init "文章标题"
python tools/progress_updater.py step "extraction" "内容提取完成"
```

## 工具来源

所有复用工具位于：
```
.claude/skills/auto-writing/tools/
```
