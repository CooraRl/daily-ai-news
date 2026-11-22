# daily-ai-news

每日抓取 AI 新闻，并生成一份 Markdown 摘要。

这是一个面向 Python 零基础学习者的开源练习项目：先用公开 RSS 源把「今天有哪些 AI 新闻」自动整理出来，后续会逐步加上数据库、FastAPI 接口、大模型摘要、RAG 问答和内容生成 Agent，作为 AI 应用开发的作品集。完整计划见 [ROADMAP.md](ROADMAP.md)。

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
├── ROADMAP.md         # 分阶段路线图与验收标准
├── .gitignore         # 忽略虚拟环境、缓存、密钥文件和生成结果
└── output/            # 运行后生成的每日 Markdown（本地目录）
```

核心逻辑都在 `main.py` 里，代码配有中文注释，建议按这个顺序阅读：

1. 文件顶部的配置：RSS 源、时区、关键词
2. `fetch_feed()`：如何用 `requests` + `feedparser` 抓取一个源
3. `pick_items()`：如何筛选「今天」的新闻
4. `write_markdown()`：如何把结果写成 Markdown

## 路线图

完整的分阶段计划（每个版本要学的技术、验收标准，以及对应的学习任务）见 **[ROADMAP.md](ROADMAP.md)**。

简要预览：

1. **V0.1（当前，Python 阶段）**：命令行脚本，抓取公开 RSS，输出标题和链接
2. **V0.2**：更多新闻源、更好的去重，用 GitHub Actions 每天自动运行
3. **V0.3**：用 SQLite / MySQL 保存历史新闻
4. **V0.4（FastAPI 阶段）**：提供 HTTP 接口，例如 `GET /news/today`
5. **V0.5（大模型阶段）**：生成中文摘要和分类，产出每日简报
6. **V0.6**：基于历史新闻库的 RAG 问答
7. **V0.7（Agent 阶段）**：自动选题，生成 X 帖子和抖音脚本草稿
8. **V0.8**：网页前端
9. **V1.0**：Docker 部署、完善文档和演示

具体任务已拆成适合初学者逐个完成的 [Issues](https://github.com/CooraRl/daily-ai-news/issues)。建议从标有 `good first issue` 的「跑通项目并精读 main.py」开始。欢迎提 Issue 或 Pull Request。

请不要把 API 密钥或密码提交到仓库。需要密钥的功能一律使用环境变量或本地 `.env`（该文件已被忽略）。

## 许可证

本项目使用 [MIT License](LICENSE)。
