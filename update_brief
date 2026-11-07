import json
import re
import html
import requests
import feedparser
from datetime import datetime, timezone

QUERIES = [
    '"Iran" AND (US OR Israel) military Gulf',
    'Iran US aircraft carrier bomber tanker Gulf',
    'Bahrain NOTAM military aviation Gulf',
    'Iran Israel military official statement'
]

RSS = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"

def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()

def collect():
    results = []
    seen = set()

    for query in QUERIES:
        try:
            url = RSS.format(requests.utils.quote(query))
            feed = feedparser.parse(url)

            for item in feed.entries[:12]:
                title = clean(item.get("title", ""))
                link = item.get("link", "")

                if not title or title.lower() in seen:
                    continue

                seen.add(title.lower())

                results.append({
                    "title": title,
                    "url": link,
                    "source": clean(
                        item.get("source", {}).get("title", "منبع خبری")
                    ),
                    "published": item.get("published", "")
                })

        except Exception as error:
            print("RSS error:", error)

    return results[:30]

def main():
    news = collect()
    items = []

    for item in news[:4]:
        items.append({
            "text": (
                item["title"]
                + " | گزارش رسانه‌ای؛ نیازمند راستی‌آزمایی مستقل."
            ),
            "url": item["url"]
        })

    if not items:
        items = [{
            "text": "در این نوبت خبر قابل دریافت از منابع انتخاب‌شده پیدا نشد.",
            "url": ""
        }]

    now = datetime.now(timezone.utc).astimezone()

    data = {
        "status": "دریافت خبر از منابع عمومی انجام شد؛ تأیید مستقل الزامی است.",
        "updated": now.isoformat(timespec="minutes"),
        "items": items,
        "source_count": len(news)
    }

    with open("latest.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print("News update completed.")

if __name__ == "__main__":
    main()
