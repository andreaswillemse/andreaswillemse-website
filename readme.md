# Andreas Willemse - Portfolio Website

## Bestanden

- `index.html` - De complete website (upload dit als hoofdbestand)
- `andreas-photo.jpg` - Profielfoto
- `sitemap.xml` - Sitemap voor zoekmachines
- `robots.txt` - Instructies voor zoekmachine crawlers
- `site.webmanifest` - Web app manifest voor mobiele apparaten
- `.htaccess` - Apache server configuratie (optioneel)

## Installatie

1. Upload alle bestanden naar je webserver root directory
2. Zorg dat `index.html` en `andreas-photo.jpg` in dezelfde map staan
3. Pas de URLs aan in de volgende bestanden (vervang `andreaswillemse.nl` door je eigen domein):
   - `index.html` (canonical URL, Open Graph, Twitter, JSON-LD)
   - `sitemap.xml`
   - `robots.txt`
   - `.htaccess` (indien je www redirect wilt)

## SEO Checklist

- [x] Meta title en description
- [x] Open Graph tags (Facebook, LinkedIn)
- [x] Twitter Card tags
- [x] Structured data (JSON-LD): WebSite, ProfilePage en Person op de homepage, BlogPosting en BreadcrumbList op elke post, NL en EN aan elkaar gekoppeld
- [x] Semantic HTML (main, article, time, aria-labels)
- [x] Sitemap.xml (gegenereerd, met hreflang en echte lastmod)
- [x] Robots.txt: AI-zoekdiensten toegelaten, crawlers voor AI-training geblokkeerd
- [x] llms.txt voor AI-zoekmachines (gegenereerd)
- [x] Favicon als bestand (favicon.ico, favicon.svg, apple-touch-icon.png), nodig voor het icoon in Google
- [x] Web manifest
- [x] Responsive design
- [x] Performance optimalisatie (.htaccess caching)

## Na livegang

1. Dien je sitemap in bij Google Search Console: https://search.google.com/search-console
2. Dien je sitemap in bij Bing Webmaster Tools: https://www.bing.com/webmasters
3. Test je structured data: https://search.google.com/test/rich-results
4. Test je Open Graph tags: https://developers.facebook.com/tools/debug/

## Vragen?

Neem contact op via LinkedIn: https://linkedin.com/in/andreaswillemse

## RSS

`blog/feed.xml` en `en/blog/feed.xml` worden bij elke Netlify-deploy automatisch gegenereerd (`netlify.toml` draait `tools/build-feeds.py`). Een nieuwe post wordt opgepikt zodra de pagina een `article:published_time` meta-tag heeft. Lokaal bijwerken: `python3 tools/build-feeds.py`.

## Sitemap en llms.txt

`sitemap.xml` en `llms.txt` worden bij elke deploy gegenereerd door `tools/build-seo.py`. Lokaal bijwerken: `python3 tools/build-seo.py`.

- Een nieuwe post komt er vanzelf in zodra hij een `article:published_time` meta-tag heeft.
- Pas je een post inhoudelijk aan, zet dan `dateModified` in de JSON-LD van die post op de nieuwe datum. Dat wordt de `lastmod` in de sitemap.
- Pas je de homepage inhoudelijk aan, zet dan `dateModified` van de `ProfilePage` in de JSON-LD van `index.html` en `en/index.html` op de nieuwe datum.
- Track record, expertise en beschikbaarheid in `llms.txt` komen uit `en/index.html`.
- Op deploy previews en branch deploys (zoals `dev`) zet het script een `X-Robots-Tag: noindex` op alle pagina's. Productie blijft indexeerbaar.
