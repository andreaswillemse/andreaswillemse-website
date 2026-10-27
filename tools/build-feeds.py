#!/usr/bin/env python3
"""Genereert blog/feed.xml (NL) en en/blog/feed.xml (EN) uit de blogposts.

Draai na het toevoegen van een post: python3 tools/build-feeds.py
"""
import glob, html, os, re
from datetime import datetime, timezone
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://andreaswillemse.nl"
FEEDS = [
    {"dir": "blog", "lang": "nl", "path": "/blog/", "title": "Blog van Andreas Willemse",
     "desc": "Artikelen over AI in productontwikkeling, digitale strategie en product management."},
    {"dir": "en/blog", "lang": "en", "path": "/en/blog/", "title": "Andreas Willemse's blog",
     "desc": "Articles on AI in product development, digital strategy and product management."},
]

def meta(src, pattern):
    m = re.search(pattern, src)
    return html.unescape(m.group(1)).strip() if m else None

for f in FEEDS:
    items = []
    for p in glob.glob(os.path.join(ROOT, f["dir"], "*.html")):
        slug = os.path.basename(p)[:-5]
        if slug == "index":
            continue
        src = open(p, encoding="utf-8").read()
        date = meta(src, r'article:published_time" content="([^"]+)"')
        if not date:
            continue
        title = re.sub(r"\s*\|\s*Andreas Willemse$", "", meta(src, r"<title>(.*?)</title>"))
        desc = meta(src, r'property="og:description" content="([^"]*)"')
        items.append((date, slug, title, desc))
    items.sort(reverse=True)

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', '<channel>',
           f'<title>{html.escape(f["title"])}</title>',
           f'<link>{SITE}{f["path"]}</link>',
           f'<description>{html.escape(f["desc"])}</description>',
           f'<language>{f["lang"]}</language>',
           f'<atom:link href="{SITE}{f["path"]}feed.xml" rel="self" type="application/rss+xml"/>']
    if items:
        newest = datetime.fromisoformat(items[0][0]).replace(hour=12, tzinfo=timezone.utc)
        out.append(f'<lastBuildDate>{format_datetime(newest)}</lastBuildDate>')
    for date, slug, title, desc in items:
        url = f'{SITE}{f["path"]}{slug}'
        pub = datetime.fromisoformat(date).replace(hour=12, tzinfo=timezone.utc)
        out += ['<item>', f'<title>{html.escape(title)}</title>', f'<link>{url}</link>',
                f'<guid isPermaLink="true">{url}</guid>',
                f'<pubDate>{format_datetime(pub)}</pubDate>',
                f'<description>{html.escape(desc or "")}</description>', '</item>']
    out += ['</channel>', '</rss>', '']
    open(os.path.join(ROOT, f["dir"], "feed.xml"), "w", encoding="utf-8").write("\n".join(out))
    print(f'{f["dir"]}/feed.xml: {len(items)} items')
