# daily-ai-news

每日抓取 AI 新闻，并生成一份 Markdown 摘要。

这是一个面向 Python 零基础学习者的开源练习项目：先用公开 RSS 源把「今天有哪些 AI 新闻」自动整理出来，后续会逐步加上 FastAPI 接口和大模型摘要 Agent，作为 AI 应用开发的作品集。

作者：[CooraRl](https://github.com/CooraRl) · X：[@XxCoora](https://x.com/XxCoora)

## 功能

- 用 `requests` 请求多个公开 RSS 源，再用 `feedparser` 解析
- 对 Hacker News 这类综合源，按标题关键词过滤出 AI 相关条目
- 按北京时间筛选「今天」的新闻；如果今天还没有新内容，会回退展示最近 2 天的条目
- 把标题和链接按来源分组，写入 `output/ai-news-YYYY-MM-DD.md`
- 不需要 API 密钥，也不依赖任何付费服务

当前默认数据源：

- Hacker News（`hnrss.org`，带 AI 关键词过滤）
- TechCrunch AI
- Hugging Face Blog
- Google AI Blog
- arXiv cs.AI（通过 arXiv API 获取最近论文，避免周末官方 RSS 为空）

## 安装与运行

需要已安装 Python 3.10 或更高版本。

```bash
# 1. 克隆仓库
git clone https://github.com/CooraRl/daily-ai-news.git
cd daily-ai-news

# 2. 创建并激活虚拟环境（推荐）
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行脚本
python main.py
```

运行成功后，会在 `output/` 目录生成当天的 Markdown 文件，例如：

```text
output/ai-news-2026-11-22.md
```

用任意文本编辑器或 Markdown 预览工具打开即可阅读。

> `output/` 已加入 `.gitignore`，生成结果默认不会被提交。如果你想把某一天的摘要也放到仓库里，可以手动把文件移出该目录后再提交。

## 项目结构

```text
daily-ai-news/
├── main.py            # 抓取与生成摘要的主脚本
├── requirements.txt   # Python 依赖
├── LICENSE            # MIT 开源许可证
├── README.md          # 项目说明
├── .gitignore         # 忽略虚拟环境、缓存和生成结果
└── output/            # 运行后生成的每日 Markdown（本地目录）
```

核心逻辑都在 `main.py` 里，代码配有中文注释，建议按这个顺序阅读：

1. 文件顶部的配置：RSS 源、时区、关键词
2. `fetch_feed()`：如何用 `requests` + `feedparser` 抓取一个源
3. `pick_items()`：如何筛选「今天」的新闻
4. `write_markdown()`：如何把结果写成 Markdown

## 路线图

这个仓库会跟着学习路线一起升级：

1. **现在（Python 阶段）**：命令行脚本，抓取公开 RSS，输出标题和链接
2. **下一步（FastAPI 阶段）**：提供 HTTP 接口，例如 `GET /news/today`，用浏览器或接口工具查看当天新闻
3. **再下一步（大模型 / Agent 阶段）**：接入大模型，把标题列表扩写成中文摘要，做成「每日 AI 新闻摘要 Agent」

欢迎提 Issue 或 Pull Request。

## 许可证

本项目使用 [MIT License](LICENSE)。
