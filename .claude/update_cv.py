#!/usr/bin/env python3
"""Zet een CV-export om in cv.html met de juiste head tags erin.

Gebruik:
    python3 .claude/update_cv.py ~/Downloads/CV_export.html

De export uit de CV-generator bevat alleen een kale <head>. Dit script plakt
het blok hieronder er weer in: noindex (de pagina bevat telefoonnummer en
e-mailadres), canonical, Open Graph voor gedeelde links, en de favicon van de
site. Draai het zo vaak je wilt: een al aanwezig blok wordt eerst verwijderd.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "cv.html"

START = "<!-- site-head-start -->"
END = "<!-- site-head-end -->"

HEAD_BLOCK = f"""{START}
<meta name="description" content="Curriculum vitae van Andreas Willemse, Senior Product Owner en Product Manager in Amsterdam.">
<meta name="author" content="Andreas Willemse">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="https://andreaswillemse.nl/cv">

<!-- Open Graph -->
<meta property="og:type" content="profile">
<meta property="og:url" content="https://andreaswillemse.nl/cv">
<meta property="og:title" content="CV Andreas Willemse - Senior Product Owner">
<meta property="og:description" content="Curriculum vitae van Andreas Willemse, Senior Product Owner en Product Manager in Amsterdam.">
<meta property="og:image" content="https://andreaswillemse.nl/andreas-photo.jpg">
<meta property="og:site_name" content="Andreas Willemse">

<!-- Favicon -->
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%231a3a2e'/><text x='50' y='70' font-size='60' text-anchor='middle' fill='%23fafafa' font-family='monospace' font-weight='bold'>AW</text></svg>">
<meta name="theme-color" content="#1a3a2e">
{END}"""


def main():
    if len(sys.argv) != 2:
        sys.exit(f"Gebruik: python3 {Path(__file__).name} <pad/naar/cv-export.html>")

    source = Path(sys.argv[1]).expanduser()
    if not source.is_file():
        sys.exit(f"Bestand niet gevonden: {source}")

    html = source.read_text(encoding="utf-8")

    if "</title>" not in html:
        sys.exit("Geen </title> gevonden — is dit wel de CV-export?")

    # Een eerder ingevoegd blok eruit, zodat herhaald draaien niet stapelt.
    html = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", html, flags=re.S)
    html = html.replace("</title>", "</title>\n" + HEAD_BLOCK, 1)

    TARGET.write_text(html, encoding="utf-8")
    print(f"cv.html bijgewerkt vanuit {source.name} ({len(html) // 1024} KB)")
    print("Controleer met: git diff --stat cv.html")


if __name__ == "__main__":
    main()
