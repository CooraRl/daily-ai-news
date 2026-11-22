#!/usr/bin/env python3
"""每日 AI 新闻抓取脚本。

从几个公开 RSS 源抓取 AI 相关新闻，筛选出「今天」的标题和链接，
并写入 Markdown 文件。不需要任何 API 密钥。

适合 Python 初学者阅读：每一步都有中文注释。

用法：
    python main.py
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import feedparser
import requests

# ---------------------------------------------------------------------------
# 可自行修改的配置
# ---------------------------------------------------------------------------

# 用北京时间判断「今天」。如果你在其他时区，改成例如 "Asia/Tokyo"。
TIMEZONE = ZoneInfo("Asia/Shanghai")

# 请求超时（秒）。某个源太慢就放弃，不影响其他源。
REQUEST_TIMEOUT = 20

# 每个源最多保留多少条，避免 Markdown 太长。
MAX_ITEMS_PER_FEED = 15

# 如果今天一条都没有，就回退展示最近几天的新闻。
FALLBACK_DAYS = 2

# 礼貌的 User-Agent，部分网站会拦截默认的 python-requests。
USER_AGENT = "daily-ai-news/0.1 (learning project; https://github.com/CooraRl/daily-ai-news)"

# 用于过滤 Hacker News 等综合源的关键词（不区分大小写）。
AI_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "llm",
    "gpt",
    "claude",
    "grok",
    "openai",
    "anthropic",
    "deepseek",
    "gemini",
    "machine learning",
    "deep learning",
    "neural",
    "transformer",
    "agent",
    "chatgpt",
    "大模型",
    "人工智能",
    "机器学习",
]

# 公开 RSS 源。filter_keywords=True 表示需要用上面的关键词过滤。
FEEDS = [
    {
        "name": "Hacker News",
        "url": "https://hnrss.org/newest?points=5",
        "filter_keywords": True,
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "filter_keywords": False,
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "filter_keywords": False,
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "filter_keywords": False,
    },
    {
        "name": "arXiv cs.AI",
        # 使用 arXiv API 的 Atom 源：周末官方 RSS 可能是空的，这个接口仍能返回最近论文。
        "url": "https://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=15&sortBy=submittedDate&sortOrder=descending",
        "filter_keywords": False,
    },
]

# 输出目录：和脚本放在同一项目下的 output/ 文件夹。
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def is_ai_related(title: str) -> bool:
    """判断标题是否包含 AI 相关关键词。

    英文关键词按「单词」匹配，避免把 Ukraine 里的 ai 误判成 AI；
    中文关键词则用普通包含判断。
    """
    lowered = title.lower()
    for keyword in AI_KEYWORDS:
        kw = keyword.lower()
        # 只要关键词里有汉字，就做子字符串匹配。
        if any("\u4e00" <= ch <= "\u9fff" for ch in kw):
            if kw in lowered:
                return True
            continue
        # 左右不能是字母或数字，这样 AI、LLM、GPT-4 都能匹配。
        pattern = r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])"
        if re.search(pattern, lowered):
            return True
    return False


def parse_entry_time(entry: dict) -> datetime | None:
    """把 RSS 条目的发布时间转成带时区的 datetime。

    feedparser 会把日期解析成 time.struct_time，放在 published_parsed
    或 updated_parsed 里。解析失败时返回 None。
    """
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    try:
        # struct_time 是世界时（UTC），前 6 项是年/月/日/时/分/秒。
        return datetime(*parsed[:6], tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def fetch_feed(feed: dict) -> list[dict]:
    """用 requests 下载 RSS，再用 feedparser 解析，返回规范化后的条目列表。"""
    name = feed["name"]
    url = feed["url"]
    print(f"正在抓取：{name} ...")

    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml, */*"},
        )
        # 状态码不是 2xx 就抛出异常，交给下面的 except 处理。
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"  抓取失败（已跳过）：{exc}")
        return []

    parsed = feedparser.parse(response.content)
    items: list[dict] = []

    for entry in parsed.entries:
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()
        if not title or not link:
            continue

        # 综合源（如 Hacker News）只保留标题里带 AI 关键词的条目。
        if feed.get("filter_keywords") and not is_ai_related(title):
            continue

        items.append(
            {
                "source": name,
                "title": title,
                "link": link,
                "published": parse_entry_time(entry),
            }
        )

        if len(items) >= MAX_ITEMS_PER_FEED:
            break

    print(f"  解析到 {len(items)} 条")
    return items


def is_today(published: datetime | None, today) -> bool:
    """判断一条新闻的发布日期是不是「今天」（按配置的时区）。"""
    if published is None:
        return False
    return published.astimezone(TIMEZONE).date() == today


def pick_items(all_items: list[dict], today) -> tuple[list[dict], str]:
    """优先选今天的新闻；如果一条都没有，就回退到最近几天。"""
    todays = [item for item in all_items if is_today(item["published"], today)]
    if todays:
        return todays, "today"

    # 没有今天的内容时，放宽到最近 FALLBACK_DAYS 天，方便你随时能跑出结果。
    cutoff = datetime.now(TIMEZONE) - timedelta(days=FALLBACK_DAYS)
    recent = []
    for item in all_items:
        published = item["published"]
        if published is None or published >= cutoff:
            recent.append(item)
    return recent, "fallback"


def format_published(published: datetime | None) -> str:
    """把时间格式化成可读的北京时间字符串。"""
    if published is None:
        return "时间未知"
    return published.astimezone(TIMEZONE).strftime("%Y-%m-%d %H:%M")


def write_markdown(items: list[dict], today, mode: str, output_path: Path) -> None:
    """把新闻列表写成 Markdown 文件。"""
    date_str = today.isoformat()
    lines = [
        f"# 每日 AI 新闻 · {date_str}",
        "",
        f"生成时间：{datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M')}（北京时间）",
        "",
    ]

    if mode == "fallback":
        lines.append(
            f"> 今天暂未抓到新内容，以下为最近 {FALLBACK_DAYS} 天内的条目（含日期未知的近期条目）。"
        )
        lines.append("")

    if not items:
        lines.append("今天没有抓到新闻，请稍后再试，或检查网络连接。")
        lines.append("")
    else:
        # 按来源分组，方便阅读。
        grouped: dict[str, list[dict]] = {}
        for item in items:
            grouped.setdefault(item["source"], []).append(item)

        total = len(items)
        lines.append(f"共 **{total}** 条，来自 {len(grouped)} 个源。")
        lines.append("")

        for source, source_items in grouped.items():
            lines.append(f"## {source}")
            lines.append("")
            for item in source_items:
                title = item["title"].replace("\n", " ").strip()
                lines.append(f"- [{title}]({item['link']})  ")
                lines.append(f"  _{format_published(item['published'])}_")
            lines.append("")

    lines.append("---")
    lines.append("由 [daily-ai-news](https://github.com/CooraRl/daily-ai-news) 自动生成。")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def deduplicate(items: list[dict]) -> list[dict]:
    """按链接去重，保留第一次出现的条目。"""
    seen: set[str] = set()
    unique: list[dict] = []
    for item in items:
        if item["link"] in seen:
            continue
        seen.add(item["link"])
        unique.append(item)
    return unique


def main() -> int:
    today = datetime.now(TIMEZONE).date()
    print(f"开始抓取每日 AI 新闻（今天是 {today}，时区：Asia/Shanghai）")
    print()

    all_items: list[dict] = []
    for feed in FEEDS:
        all_items.extend(fetch_feed(feed))

    all_items = deduplicate(all_items)
    selected, mode = pick_items(all_items, today)

    output_path = OUTPUT_DIR / f"ai-news-{today.isoformat()}.md"
    write_markdown(selected, today, mode, output_path)

    print()
    if mode == "today":
        print(f"已写入今天的 {len(selected)} 条新闻：{output_path}")
    else:
        print(f"今天暂无新内容，已写入最近 {FALLBACK_DAYS} 天内的 {len(selected)} 条：{output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
