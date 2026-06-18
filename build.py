#!/usr/bin/env python3
"""
build.py - Programmatic-SEO static site generator for StatusCode.dev

Stdlib only. Reads data.json and emits a complete static site into ./public/:
  - one reference page per HTTP status code      (/<code>.html)
  - one category hub page per class (1xx..5xx)    (/category/<class>.html)
  - a homepage index with internal links          (/index.html)
  - sitemap.xml and robots.txt

Run:  python3 build.py
"""

import json
import os
import html
import datetime
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data.json")
OUT = os.path.join(ROOT, "public")

# Path prefix for internal links. GitHub Pages project sites serve under
# /<repo>/ (e.g. /contentsite), so internal hrefs must be prefixed or they 404.
# Set data.json "path_prefix" to "" once a custom domain serves from root.
_PP = os.environ.get("PATH_PREFIX")
def _prefix(site):
    p = _PP if _PP is not None else site.get("path_prefix", "")
    return p.rstrip("/")

# ---- AdSense / affiliate placeholders (clearly marked) -----------------------
# The human inserts their real AdSense code where ADSENSE_SLOT appears, and swaps
# the affiliate ref codes in data.json. Until then these are inert placeholders.
ADSENSE_SLOT = """<!-- ADSENSE_SLOT: paste your AdSense auto-ad or in-article unit here -->
<div class="ad" aria-hidden="true" data-ad-placeholder="true">
  <!-- ADSENSE_SLOT_START -->
  <!-- <ins class="adsbygoogle" style="display:block" data-ad-client="{pub}"
       data-ad-slot="0000000000" data-ad-format="auto"></ins> -->
  <span class="ad-label">Advertisement</span>
  <!-- ADSENSE_SLOT_END -->
</div>"""


def esc(s):
    return html.escape(str(s), quote=True)


def klass(code):
    return f"{code // 100}xx"


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


# ---- HTML scaffolding --------------------------------------------------------

def page_shell(site, *, title, description, canonical, body, jsonld=None,
               adsense_head=True):
    pub = site["adsense_publisher_id"]
    adsense_head_tag = ""
    if adsense_head:
        adsense_head_tag = (
            "<!-- ADSENSE_HEAD: uncomment after AdSense approval and set your pub id -->\n"
            f'    <!-- <script async src="https://pagead2.googlesyndication.com/'
            f'pagead/js/adsbygoogle.js?client={esc(pub)}" crossorigin="anonymous">'
            "</script> -->"
        )
    jsonld_tag = ""
    if jsonld:
        jsonld_tag = (
            '<script type="application/ld+json">'
            + json.dumps(jsonld, ensure_ascii=False)
            + "</script>"
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{esc(canonical)}">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{esc(canonical)}">
    <meta name="robots" content="index,follow">
    {adsense_head_tag}
    {jsonld_tag}
    <style>
      :root{{--fg:#1a1a2e;--mut:#5b6270;--acc:#2d6cdf;--bg:#fff;--card:#f6f8fc;--line:#e3e8f0}}
      *{{box-sizing:border-box}}
      body{{margin:0;font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--fg);background:var(--bg)}}
      header,main,footer{{max-width:860px;margin:0 auto;padding:0 20px}}
      header{{padding-top:22px}}
      a{{color:var(--acc);text-decoration:none}} a:hover{{text-decoration:underline}}
      .brand{{font-weight:700;font-size:20px}}
      nav{{font-size:14px;color:var(--mut);margin:6px 0 18px}}
      h1{{font-size:1.9rem;line-height:1.2;margin:.2em 0}}
      .code-badge{{display:inline-block;font-size:.8rem;font-weight:700;padding:2px 10px;border-radius:999px;background:var(--acc);color:#fff;vertical-align:middle}}
      .lead{{font-size:1.12rem;color:var(--mut)}}
      .card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:16px 0}}
      .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:14px 0}}
      .grid a{{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}}
      .grid .n{{font-weight:700}} .grid .d{{font-size:.82rem;color:var(--mut)}}
      .meta{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}
      .pill{{font-size:.78rem;padding:2px 9px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--mut)}}
      .ad{{border:1px dashed #c6cfdd;border-radius:10px;min-height:90px;display:flex;align-items:center;justify-content:center;margin:22px 0;background:repeating-linear-gradient(45deg,#fafbfe,#fafbfe 10px,#f2f5fb 10px,#f2f5fb 20px)}}
      .ad-label{{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:#9aa3b2}}
      .aff{{font-size:.9rem;margin:6px 0}}
      table{{border-collapse:collapse;width:100%;font-size:.95rem}}
      td,th{{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left}}
      footer{{color:var(--mut);font-size:.85rem;border-top:1px solid var(--line);margin-top:40px;padding:20px 20px 50px}}
    </style>
</head>
<body>
{body}
</body>
</html>"""


def affiliate_block(site):
    rows = "\n".join(
        f'      <p class="aff">\u2192 <a rel="sponsored nofollow" href="{esc(a["url"])}">'
        f'{esc(a["label"])}</a></p>'
        for a in site["_affiliates"]
    )
    return f"""    <div class="card">
      <!-- AFFILIATE_BLOCK: swap the ref codes in data.json for your own -->
      <strong>{esc(site['affiliate_blurb'])}</strong>
{rows}
    </div>"""


def header_html(site, breadcrumb):
    pp = _prefix(site)
    return f"""<header>
  <div class="brand"><a href="{pp}/">{esc(site['name'])}</a></div>
  <nav>{breadcrumb}</nav>
</header>"""


def footer_html(site):
    yr = datetime.date.today().year
    return f"""<footer>
  <p>{esc(site['name'])} \u2014 {esc(site['tagline'])}.</p>
  <p>Data compiled from the HTTP specification (RFC 9110 et al.). &copy; {yr}.
     <a href="{_prefix(site)}/sitemap.xml">Sitemap</a></p>
</footer>"""


# ---- Page builders -----------------------------------------------------------

def build_code_page(site, c):
    code = c["code"]
    cls = klass(code)
    cat_desc = site["categories"][cls]
    cat_short = cat_desc.split(" \u2013 ")[0]
    url = f"{site['base_url']}/{code}.html"
    title = f"HTTP {code} {c['name']} \u2013 Meaning, Causes & How to Fix"
    desc = f"What HTTP status code {code} ({c['name']}) means: {c['summary']} Common causes and how to fix it."
    pp = _prefix(site)
    breadcrumb = (f'<a href="{pp}/">Home</a> &rsaquo; '
                  f'<a href="{pp}/category/{cls}.html">{cls} {esc(cat_short)}</a> '
                  f'&rsaquo; {code}')

    related = [x for x in site["codes"] if klass(x["code"]) == cls and x["code"] != code][:6]
    related_html = "\n".join(
        f'      <a href="{pp}/{r["code"]}.html"><span class="n">{r["code"]}</span>'
        f'<span class="d">{esc(r["name"])}</span></a>'
        for r in related
    )

    jsonld = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": title,
        "description": c["summary"],
        "about": {"@type": "Thing", "name": f"HTTP {code} {c['name']}"},
        "author": {"@type": "Organization", "name": site["author"]},
        "mainEntityOfPage": url,
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f"What does HTTP {code} mean?",
             "acceptedAnswer": {"@type": "Answer", "text": c["summary"]}},
            {"@type": "Question", "name": f"How do I fix a {code} {c['name']} error?",
             "acceptedAnswer": {"@type": "Answer", "text": c["fix"]}},
        ],
    }

    body = f"""{header_html(site, breadcrumb)}
<main>
  <h1><span class="code-badge">{code}</span> {esc(c['name'])}</h1>
  <p class="lead">{esc(c['summary'])}</p>
  <div class="meta">
    <span class="pill">Class: {cls} {esc(cat_short)}</span>
    <span class="pill">Cacheable: {'yes' if c['cacheable'] else 'no'}</span>
    <span class="pill">Safe to retry: {'yes' if c['retry'] else 'no'}</span>
  </div>

  {ADSENSE_SLOT.format(pub=esc(site['adsense_publisher_id']))}

  <div class="card">
    <h2>When you see HTTP {code}</h2>
    <p>{esc(c['when'])}</p>
  </div>
  <div class="card">
    <h2>How to fix {code} {esc(c['name'])}</h2>
    <p>{esc(c['fix'])}</p>
  </div>

{affiliate_block(site)}

  <h2>Other {cls} status codes</h2>
  <div class="grid">
{related_html}
  </div>
  <p><a href="{pp}/category/{cls}.html">See all {cls} codes &rarr;</a> &middot; <a href="{pp}/">All HTTP status codes</a></p>
</main>
{footer_html(site)}"""
    return page_shell(site, title=title, description=desc, canonical=url,
                      body=body, jsonld=[jsonld, faq])


def build_category_page(site, cls):
    cat_desc = site["categories"][cls]
    url = f"{site['base_url']}/category/{cls}.html"
    short = cat_desc.split(" \u2013 ")[0]
    title = f"{cls} HTTP Status Codes \u2013 {short} (Full List)"
    desc = f"Complete list of {cls} HTTP status codes. {cat_desc}."
    pp = _prefix(site)
    breadcrumb = f'<a href="{pp}/">Home</a> &rsaquo; {cls} {esc(short)}'
    codes = [c for c in site["codes"] if klass(c["code"]) == cls]
    cards = "\n".join(
        f'      <a href="{pp}/{c["code"]}.html"><span class="n">{c["code"]} {esc(c["name"])}</span>'
        f'<span class="d">{esc(c["summary"][:70])}\u2026</span></a>'
        for c in codes
    )
    jsonld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": desc,
        "url": url,
    }
    body = f"""{header_html(site, breadcrumb)}
<main>
  <h1>{cls} \u2013 {esc(short)}</h1>
  <p class="lead">{esc(cat_desc)}.</p>
  {ADSENSE_SLOT.format(pub=esc(site['adsense_publisher_id']))}
  <div class="grid">
{cards}
  </div>
  <p><a href="{pp}/">&larr; All HTTP status codes</a></p>
</main>
{footer_html(site)}"""
    return page_shell(site, title=title, description=desc, canonical=url,
                      body=body, jsonld=jsonld)


def build_index(site):
    pp = _prefix(site)
    url = site["base_url"] + "/"
    title = f"{site['name']} \u2013 HTTP Status Codes Reference (Complete List)"
    desc = ("Complete, fast HTTP status code reference. Look up the meaning, common "
            "causes, and fixes for every HTTP response code from 100 to 511.")
    sections = []
    for cls, cat_desc in site["categories"].items():
        codes = [c for c in site["codes"] if klass(c["code"]) == cls]
        if not codes:
            continue
        cards = "\n".join(
            f'      <a href="{pp}/{c["code"]}.html"><span class="n">{c["code"]}</span>'
            f'<span class="d">{esc(c["name"])}</span></a>'
            for c in codes
        )
        short = cat_desc.split(" \u2013 ")[0]
        sections.append(
            f'  <h2 id="{cls}"><a href="{pp}/category/{cls}.html">{cls} \u2013 {esc(short)}</a></h2>\n'
            f'  <p style="color:#5b6270;margin-top:0">{esc(cat_desc)}.</p>\n'
            f'  <div class="grid">\n{cards}\n  </div>'
        )
    jsonld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site["name"],
        "url": url,
        "description": desc,
    }
    body = f"""{header_html(site, '')}
<main>
  <h1>HTTP Status Codes \u2013 Complete Reference</h1>
  <p class="lead">{esc(site['tagline'])}. Click any code for its meaning, causes, and how to fix it.</p>
  {ADSENSE_SLOT.format(pub=esc(site['adsense_publisher_id']))}
{chr(10).join(sections)}
{affiliate_block(site)}
</main>
{footer_html(site)}"""
    return page_shell(site, title=title, description=desc, canonical=url,
                      body=body, jsonld=jsonld)


def build_sitemap(site, urls):
    today = datetime.date.today().isoformat()
    items = "\n".join(
        f"  <url><loc>{esc(u)}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>monthly</changefreq></url>"
        for u in urls
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{items}\n</urlset>\n")


def build_robots(site):
    return (f"User-agent: *\nAllow: /\n\nSitemap: {site['base_url']}/sitemap.xml\n")


# ---- Driver ------------------------------------------------------------------

def main():
    data = load()
    site = data["site"]
    site["categories"] = data["categories"]
    site["codes"] = sorted(data["codes"], key=lambda c: c["code"])
    site["_affiliates"] = data["affiliates"]

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "category"), exist_ok=True)

    urls = [site["base_url"] + "/"]
    count = 0

    # index
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_index(site))
    count += 1

    # per-code pages
    for c in site["codes"]:
        path = os.path.join(OUT, f"{c['code']}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_code_page(site, c))
        urls.append(f"{site['base_url']}/{c['code']}.html")
        count += 1

    # category hubs
    used = sorted({klass(c["code"]) for c in site["codes"]})
    for cls in used:
        path = os.path.join(OUT, "category", f"{cls}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_category_page(site, cls))
        urls.append(f"{site['base_url']}/category/{cls}.html")
        count += 1

    # sitemap + robots
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(build_sitemap(site, urls))
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(build_robots(site))

    print(f"Generated {count} HTML pages "
          f"({len(site['codes'])} code pages + {len(used)} category hubs + 1 index)")
    print(f"+ sitemap.xml ({len(urls)} URLs) + robots.txt")
    print(f"Output: {OUT}")


if __name__ == "__main__":
    main()
