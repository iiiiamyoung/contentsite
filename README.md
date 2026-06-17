# StatusCode.dev — Programmatic-SEO HTTP Status Code Reference

A static-site generator that builds a complete HTTP status code reference site from a
dataset. Pure Python stdlib, no dependencies, generates SEO-friendly static HTML you can
deploy free to Cloudflare Pages or GitHub Pages.

```
python3 build.py            # reads data.json -> writes ./public/
```

Output (this run): **40 HTML pages** = 34 per-code pages + 5 category hubs + 1 index,
plus `sitemap.xml` and `robots.txt`.

---

## The niche: "HTTP status code meaning / how to fix"

**Why this niche:**

- **Real, durable, high-volume demand.** Developers and non-developers Google things like
  `404 meaning`, `503 error`, `what is http 429`, `301 vs 302`, `how to fix 502 bad gateway`
  constantly. These are evergreen, intent-rich queries that recur forever because the HTTP
  spec doesn't change. ("http status codes" and individual codes like "404"/"502" draw very
  large monthly search volume — verify exact numbers in Google Keyword Planner / Ahrefs
  before committing.)
- **Programmatic SEO fit.** The dataset is finite, fully *knowable from the spec* (RFC 9110
  et al.), and needs **no scraping of blocked sites**. One template → many pages, each
  targeting a distinct keyword (`http 404`, `http 502`, …). That's textbook programmatic SEO.
- **Monetizable audience.** The readers are developers and ops people — an audience that
  display advertisers (cloud, monitoring, dev tools) pay relatively high CPMs to reach, and
  that converts on affiliate offers (hosting, APM/monitoring, API tooling).
- **Defensible-ish via depth.** Thin "definition only" pages get filtered by Google and
  rejected by AdSense. Each page here carries: definition, *when you see it*, *how to fix it*,
  cacheable/retry metadata, FAQ schema, and internal links — enough substance to be useful,
  not doorway spam.

**Honest competition note:** this is a *competitive* niche (MDN, HTTP spec mirrors,
developer.mozilla.org, httpstatuses.com, etc. already rank). A new site won't outrank MDN for
the head term. The realistic play is long-tail + better UX ("how to fix 502 behind nginx",
"301 vs 308 difference") and being faster/cleaner than the cluttered competitors.

---

## What's automated vs manual

| | |
|---|---|
| **Automated** | HTML generation for every code, category hubs, index, internal linking, `<title>`/meta/canonical/OG tags, schema.org JSON-LD (TechArticle + FAQPage), `sitemap.xml`, `robots.txt`. Re-run `build.py` anytime you edit `data.json`. |
| **Manual (one-time)** | Buy a domain; deploy to Cloudflare Pages / GitHub Pages; apply for AdSense; paste your publisher ID + ad slot; swap affiliate ref codes; submit sitemap to Google Search Console & Bing Webmaster. |
| **Manual (ongoing)** | Expand `data.json` with more long-tail pages (framework-specific fixes, "X vs Y" comparisons); build backlinks; monitor Search Console; refresh content. SEO is not "set and forget". |

---

## How the human monetizes

1. **Deploy free.** Push `./public/` to GitHub and connect **Cloudflare Pages** or
   **GitHub Pages** (both free, fast, HTTPS, global CDN). Set the custom domain.
2. **Get indexed.** Add the site to **Google Search Console** + **Bing Webmaster Tools** and
   submit `sitemap.xml`. Indexing of a new site takes days to weeks.
3. **Apply for AdSense** *after* you have real content and some organic traffic (AdSense
   rejects empty/thin/no-traffic sites). Once approved:
   - Put your real `ca-pub-...` ID in `data.json` (`adsense_publisher_id`).
   - Uncomment the `<!-- ADSENSE_HEAD -->` script in `build.py`'s `page_shell`.
   - Replace each `<!-- ADSENSE_SLOT -->` placeholder with a real ad unit (or just enable
     Auto Ads). Re-run `build.py`.
4. **Affiliate (optional, often better early money).** Swap the `YOUR_REF` codes in
   `data.json` `affiliates` for real referral links (hosting, APM, API tooling). These pay
   per signup and don't need AdSense approval. Links are already marked `rel="sponsored nofollow"`.
5. **Resubmit** the sitemap whenever you add pages.

**Placeholders are clearly marked** so monetization is opt-in and reviewable:
`<!-- ADSENSE_HEAD -->`, `<!-- ADSENSE_SLOT -->` (with START/END), `<!-- AFFILIATE_BLOCK -->`.

---

## Realistic revenue expectations & timeline (honest)

**This is a real, legitimate asset pattern — but it is *not* fast or guaranteed money.**

- **Months 0–3:** Effectively $0. New domains sit in a "sandbox"; Google barely ranks them.
  AdSense may reject you until there's content + traffic. Your job here is to publish, get
  indexed, and start earning backlinks.
- **Months 3–9:** *If* pages start ranking on long-tail terms, you might see hundreds to a
  few thousand visits/month. At developer-niche RPMs (~$2–$15 per 1,000 pageviews) that is
  realistically **single-digit to low-double-digit dollars/month** from ads. Affiliate can
  add more *if* the offers match intent.
- **Months 9–24:** A site that actually gains traction in a niche like this might reach low
  thousands of visits/month and **tens of dollars/month**, occasionally more. Breakout
  results exist but are the exception, not the expectation.

**Hard truths:**
- 40 pages is a seed, not a finished site. Winning programmatic-SEO sites usually have
  hundreds–thousands of genuinely useful pages and earned backlinks.
- This niche is **competitive** (MDN dominates). Expect to win long-tail, not head terms.
- Programmatic SEO done lazily = thin/doorway pages = Google "scaled content abuse"
  penalties + AdSense rejection. The depth per page here is the minimum bar; add more.
- **Most realistic honest verdict:** this generator produces a deployable, legitimate site
  that *can* earn a small passive trickle (think coffee money) after 6–18 months of indexing,
  content expansion, and link-building — with a real but modest chance of growing into
  meaningful income, and a real chance of earning ~nothing if it never ranks. It is a
  low-cost, low-risk experiment (≈$10/yr domain, $0 hosting), not a money printer.

---

## Files

```
contentsite/
├── build.py        # stdlib-only generator
├── data.json       # the dataset (codes, categories, site config, affiliates)
├── README.md       # this file
└── public/         # generated site (deploy this dir)
    ├── index.html
    ├── <code>.html         x34
    ├── category/<class>.html  x5
    ├── sitemap.xml
    └── robots.txt
```

### Extending
Add entries to `data.json` `codes` (or add new datasets/templates for adjacent niches:
cron expressions, MIME types, TCP/UDP ports, regex cheats). Re-run `python3 build.py`.
More *genuinely useful* pages = more long-tail surface area = more traffic potential.
