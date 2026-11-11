#!/usr/bin/env python3
"""Genereert sitemap.xml en llms.txt uit de pagina's, en zet noindex op Netlify-previews.

Draait bij elke Netlify-deploy (zie netlify.toml). Lokaal: python3 tools/build-seo.py

- Een post komt in de sitemap en in llms.txt zodra hij een article:published_time meta-tag heeft.
- lastmod van een post is dateModified uit de JSON-LD. Pas die aan bij een inhoudelijke wijziging.
  Datums in de JSON-LD hebben een tijd en tijdzone (2026-10-06T00:00:00+02:00), anders waarschuwt
  Google. In de sitemap komt alleen de datum.
- lastmod van de homepage is dateModified van de ProfilePage in de JSON-LD van index.html,
  of de datum van de nieuwste post als die later is.
- Track record, expertise en beschikbaarheid in llms.txt komen uit en/index.html.
"""
import glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://andreaswillemse.nl"
LANGS = {"nl": {"home": "/", "blog": "/blog/"}, "en": {"home": "/en/", "blog": "/en/blog/"}}


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def text(fragment):
    """HTML-fragment naar platte tekst op één regel."""
    t = re.sub(r"<[^>]+>", "", fragment)
    t = html.unescape(t).replace("­", "")
    return re.sub(r"\s+", " ", t).strip()


def json_ld(src):
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)
    if not m:
        return []
    data = json.loads(m.group(1))
    return data.get("@graph", [data])


def posts(lang):
    folder = "blog" if lang == "nl" else "en/blog"
    found = {}
    for path in glob.glob(os.path.join(ROOT, folder, "*.html")):
        slug = os.path.basename(path)[:-5]
        if slug == "index":
            continue
        src = read(os.path.relpath(path, ROOT))
        published = re.search(r'article:published_time" content="([^"]+)"', src)
        if not published:
            continue
        nodes = [n for n in json_ld(src) if n.get("@type") == "BlogPosting"]
        modified = nodes[0].get("dateModified") if nodes else None
        title = re.sub(r"\s*\|\s*Andreas Willemse$", "", text(re.search(r"<title>(.*?)</title>", src, re.S).group(1)))
        desc = re.search(r'<meta name="description" content="([^"]*)"', src)
        found[slug] = {
            "slug": slug,
            "url": f"{SITE}{LANGS[lang]['blog']}{slug}",
            "title": title,
            "desc": html.unescape(desc.group(1)) if desc else "",
            "published": published.group(1),
            "modified": max((modified or "")[:10], published.group(1)[:10]),
        }
    return sorted(found.values(), key=lambda p: p["published"], reverse=True)


def home_modified():
    for node in json_ld(read("index.html")):
        if node.get("@type") == "ProfilePage" and node.get("dateModified"):
            return node["dateModified"][:10]
    return None


def build_sitemap(all_posts):
    newest = max((p["modified"] for ps in all_posts.values() for p in ps), default=None)
    home = max(filter(None, [home_modified(), newest]))

    def url(loc, lastmod, alternates):
        lines = ["  <url>", f"    <loc>{loc}</loc>"]
        for lang, href in alternates:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{href}" />')
        if alternates:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{alternates[0][1]}" />')
        lines += [f"    <lastmod>{lastmod}</lastmod>", "  </url>"]
        return lines

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    home_alts = [(l, SITE + LANGS[l]["home"]) for l in LANGS]
    blog_alts = [(l, SITE + LANGS[l]["blog"]) for l in LANGS]
    for lang in LANGS:
        out += url(SITE + LANGS[lang]["home"], home, home_alts)
    for lang in LANGS:
        blog_date = max((p["modified"] for p in all_posts[lang]), default=home)
        out += url(SITE + LANGS[lang]["blog"], blog_date, blog_alts)
    by_slug = {lang: {p["slug"]: p for p in all_posts[lang]} for lang in LANGS}
    for lang in LANGS:
        for p in all_posts[lang]:
            alts = [(l, by_slug[l][p["slug"]]["url"]) for l in LANGS if p["slug"] in by_slug[l]]
            out += url(p["url"], p["modified"], alts if len(alts) > 1 else [])
    out += ["</urlset>", ""]
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print(f"sitemap.xml: {sum(1 for line in out if line == '  <url>')} urls")


def homepage_facts():
    """Track record, expertise, beschikbaarheid en introductie uit de Engelse homepage."""
    src = read("en/index.html")
    facts = {}
    m = re.search(r'class="hero-description">(.*?)</p>', src, re.S)
    facts["intro"] = text(m.group(1)) if m else ""
    m = re.search(r'class="availability-banner">(.*?)</div>', src, re.S)
    parts = re.split(r'<span class="banner-sep">.*?</span>', m.group(1)) if m else []
    facts["availability"] = "".join(f"{text(p).rstrip('.')}. " for p in parts if text(p)).strip()
    facts["experience"] = []
    for block in re.findall(r'<article class="experience-item">(.*?)</article>', src, re.S):
        get = lambda cls: (lambda m: text(m.group(1)) if m else "")(re.search(rf'class="{cls}"[^>]*>(.*?)</(?:div|h3|p)>', block, re.S))
        facts["experience"].append({k: get(f"experience-{k}") for k in ("period", "title", "company", "result")})
    facts["skills"] = [(text(n), text(d)) for n, d in re.findall(
        r'class="skill-name">(.*?)</h3>\s*<p class="skill-description">(.*?)</p>', src, re.S)]
    for key in ("intro", "availability", "experience", "skills"):
        if not facts[key]:
            print(f"llms.txt: waarschuwing, '{key}' niet gevonden in en/index.html", file=sys.stderr)
    return facts


def build_llms(all_posts):
    f = homepage_facts()
    out = [
        "# Andreas Willemse",
        "",
        "> Freelance Product Owner and Product Manager based in Amsterdam, the Netherlands. "
        "15+ years of experience in digital product development for healthcare, retail and the (semi-)public sector. "
        "PSPO II certified.",
        "",
    ]
    if f["intro"]:
        out += [f["intro"], ""]
    out += [
        "This site is bilingual: Dutch at https://andreaswillemse.nl/ and English at https://andreaswillemse.nl/en/. "
        "Every article exists in both languages.",
        "",
    ]
    if f["availability"]:
        out += [f"Availability: {f['availability']}", ""]
    if f["experience"]:
        out += ["## Track record", ""]
        for e in f["experience"]:
            line = f"- {e['period']}: {e['title']}, {e['company']}."
            out.append(f"{line} {e['result']}" if e["result"] else line)
        out.append("")
    if f["skills"]:
        out += ["## Expertise", ""]
        out += [f"- {name}: {desc}" for name, desc in f["skills"]]
        out.append("")
    out += ["## Articles (English)", ""]
    out += [f"- [{p['title']}]({p['url']}): {p['desc']}" for p in all_posts["en"]]
    out += ["", "## Artikelen (Nederlands)", ""]
    out += [f"- [{p['title']}]({p['url']}): {p['desc']}" for p in all_posts["nl"]]
    out += [
        "",
        "## Contact",
        "",
        "- [LinkedIn](https://www.linkedin.com/in/andreaswillemse): the preferred way to get in touch",
        "",
        "## Optional",
        "",
        f"- [Homepage (English)]({SITE}/en/)",
        f"- [Homepage (Nederlands)]({SITE}/)",
        f"- [RSS feed (English)]({SITE}/en/blog/feed.xml)",
        f"- [RSS-feed (Nederlands)]({SITE}/blog/feed.xml)",
        "",
    ]
    with open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print(f"llms.txt: {len(all_posts['en']) + len(all_posts['nl'])} articles")


def noindex_previews():
    """Deploy previews en branch deploys (zoals dev) uit de zoekresultaten houden.

    Alleen bij een expliciete preview-context, zodat productie nooit noindex krijgt.
    """
    if os.environ.get("CONTEXT") not in ("deploy-preview", "branch-deploy"):
        return
    with open(os.path.join(ROOT, "_headers"), "a", encoding="utf-8") as fh:
        fh.write("\n# Toegevoegd door tools/build-seo.py: previews niet indexeren.\n/*\n  X-Robots-Tag: noindex\n")
    print(f"_headers: noindex voor context {os.environ['CONTEXT']}")


if __name__ == "__main__":
    all_posts = {lang: posts(lang) for lang in LANGS}
    build_sitemap(all_posts)
    build_llms(all_posts)
    noindex_previews()
