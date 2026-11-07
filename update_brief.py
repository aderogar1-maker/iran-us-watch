import json
import re
import html
import time
import requests
import feedparser

from datetime import datetime, timezone
from urllib.parse import quote

QUERIES = [
    '"Iran" AND (US OR Israel) military Gulf',
    'Iran US aircraft carrier bomber tanker Gulf',
    'Bahrain NOTAM military aviation Gulf',
    'Iran Israel military official statement',
    'Iran military tensions Gulf US forces'
]

RSS = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(
        r"\s+", " ",
        html.unescape(text)
    ).strip()


def translate_to_persian(text):
    if not text:
        return ""

    try:
        url = (
            "https://translate.googleapis.com/translate_a/single"
            "?client=gtx&sl=auto&tl=fa&dt=t&q="
            + quote(text)
        )

        response = session.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()

        translated = "".join(
            part[0] for part in data[0] if part[0]
        )

        return translated.strip()

    except Exception as error:
        print("Translation error:", error)
        return text


def collect():
    results = []
    seen = set()

    for query in QUERIES:
        try:
            url = RSS.format(quote(query))
            feed = feedparser.parse(url)

            for item in feed.entries[:10]:
                title = clean(item.get("title", ""))
                link = item.get("link", "")

                if not title or title.lower() in seen:
                    continue

                seen.add(title.lower())

                source = clean(
                    item.get("source", {}).get(
                        "title", "منبع خبری"
                    )
                )

                summary = clean(
                    item.get("summary", "")
                )

                results.append({
                    "title": title,
                    "summary": summary,
                    "url": link,
                    "source": source,
                    "published": item.get("published", "")
                })

        except Exception as error:
            print("RSS error:", error)

    return results[:20]


def main():
    news = collect()
    items = []

    for item in news[:8]:

        original_title = item["title"]
        original_summary = item["summary"]

        persian_title = translate_to_persian(
            original_title
        )

        persian_summary = ""

        if original_summary:
            persian_summary = translate_to_persian(
                original_summary[:700]
            )

        text = "📰 " + persian_title

        if persian_summary:
            text += "\n" + persian_summary

        text += "\nمنبع: " + item["source"]

        if item["published"]:
            text += "\nزمان انتشار: " + item["published"]

        items.append({
            "text": text,
            "url": item["url"],
            "original_title": original_title,
            "source": item["source"],
            "published": item["published"]
        })

        time.sleep(0.5)

    if not items:
        items = [{
            "text": "در این نوبت خبری از منابع انتخاب‌شده دریافت نشد.",
            "url": ""
        }]

    now = datetime.now(
        timezone.utc
    ).astimezone()

    data = {
        "status": "دریافت خبر انجام شد؛ ترجمه فارسی فعال است.",
        "updated": now.isoformat(timespec="minutes"),
        "items": items,
        "source_count": len(news)
    }

    with open(
        "latest.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("Persian news update completed.")
    print("News count:", len(items))


if __name__ == "__main__":
    main()
