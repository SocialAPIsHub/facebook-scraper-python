# facebook-scraper-python

[![PyPI](https://badge.fury.io/py/socialapis-sdk.svg)](https://pypi.org/project/socialapis-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/socialapis-sdk)](https://pypi.org/project/socialapis-sdk/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Modern Python alternative to [`kevinzg/facebook-scraper`](https://github.com/kevinzg/facebook-scraper) — the 9.5k-star library that's been **abandoned since 2022**. Hosted backend means it doesn't break every time Meta changes their HTML.

This repo is a **migration landing page** + working examples. The actual SDK lives at [`SocialAPIsHub/socialapis-python`](https://github.com/SocialAPIsHub/socialapis-python) and ships as the `socialapis-sdk` package on PyPI.

```bash
pip install socialapis-sdk
```

```python
from socialapis import FacebookScraper

fb = FacebookScraper(api_token="...")           # alias of Facebook — keeps your import line greppable
page = fb.get_page_info("EngenSA")
print(page.title, page.followers_count, page.category)

for post in fb.get_page_posts("EngenSA").get("posts", []):
    print(post["text"][:80])
```

**[Get a free API token →](https://socialapis.io/auth/signup)** — 200 calls/month, no credit card

---

## Why this exists

[`kevinzg/facebook-scraper`](https://github.com/kevinzg/facebook-scraper) was the default Python library for scraping Facebook for years. 9.5k+ GitHub stars. It's been **abandoned since 2022** — open issues pile up, PRs sit unmerged, and every Meta DOM change breaks it.

If you're here because:

- `facebook-scraper` stopped returning data
- You searched for "facebook-scraper alternative" or "kevinzg fork"
- Your `get_posts()` calls started raising `TemporarilyBanned` or returning empty lists
- You're tired of patching a library nobody maintains

…this is the modern replacement. Same idea — Facebook public data via Python — but the actual scraping runs on a hosted API ([socialapis.io](https://socialapis.io)) so you never debug Meta's HTML again.

## Side-by-side migration

```python
# BEFORE — kevinzg/facebook-scraper (abandoned)
from facebook_scraper import get_page_info, get_posts

page = get_page_info("EngenSA")
print(page["name"], page["likes"])

for post in get_posts("EngenSA", pages=5):
    print(post["time"], post["text"][:80])
```

```python
# AFTER — socialapis (one import line changed)
from socialapis import FacebookScraper          # alias of Facebook

fb = FacebookScraper(api_token="...")
page = fb.get_page_info("EngenSA")
print(page.title, page.likes_count)             # typed Pydantic model, IDE autocomplete

for post in fb.get_page_posts("EngenSA").get("posts", []):
    print(post.get("time"), post.get("text", "")[:80])
```

`FacebookScraper` is an exact alias of `socialapis.Facebook` — same class, same methods, just a different name so your grep-replace migration stays a one-liner.

## Method-by-method mapping

| `kevinzg/facebook-scraper` | `socialapis` (this SDK) |
|---|---|
| `get_page_info(page)` | `FacebookScraper(api_token=…).get_page_info(page)` |
| `get_posts(page, pages=N)` | `FacebookScraper(…).get_page_posts(page)` |
| `get_group_info(group)` | `FacebookScraper(…).get_group_details(group)` |
| `get_friends(user)` | (Meta blocked it years ago — even kevinzg deprecated it) |
| `set_proxy(...)` / `set_user_agent(...)` | Not needed — we manage the scraping infra |
| `set_cookies(...)` | Not needed — no Facebook login required |

Full working example: [`examples/migrate.py`](examples/migrate.py).

## What you get on top of the kevinzg surface

The hosted backend supports more than kevinzg ever did. From the same `FacebookScraper` instance:

```python
# Group posts + metadata
fb.get_group_details("groupslug")
fb.get_group_posts("groupslug")

# Search — pages, people, posts, videos, locations
fb.search_pages("marketing", location_id="103006566409959")
fb.search_posts("nike", recency="last_month")

# Meta Ads Library (full transparency data — creative, spend, impressions)
fb.search_ads("fitness", country="US", activeStatus="Active")
fb.get_ad_archive_details(ad_archive_id="...", page_id="...")

# Marketplace (listings, vehicles, rentals)
fb.search_marketplace("cars", filter_location_latitude="40.7142", filter_location_longitude="-74.0064")
fb.get_listing_details("123456789")

# Reels
fb.get_page_reels("EngenSA")

# Async — same surface, methods are coroutines
from socialapis import AsyncFacebookScraper
async with AsyncFacebookScraper(api_token="…") as fb:
    page = await fb.get_page_info("EngenSA")
```

Full method list + Pydantic response types: [main SDK README →](https://github.com/SocialAPIsHub/socialapis-python#readme)

## Comparison at a glance

| | `kevinzg/facebook-scraper` (2018-era) | `socialapis` (2026) |
|---|---|---|
| **Maintenance** | Abandoned 2022 | Active; 7M+ calls/month in prod |
| **Reliability** | Breaks on every Meta HTML change | Hosted backend; we absorb breakage |
| **Type hints** | None | Strict; Pydantic v2 models |
| **Async** | No | `Facebook` + `AsyncFacebook` classes |
| **HTTP client** | `requests` | `httpx` |
| **Auth** | None (anonymous, often rate-limited) | Single `x-api-token` header, 200 free calls/month |
| **Pagination** | Generator with edge-case bugs | Cursor-based; API decides page size |
| **Error handling** | Generic exceptions | Typed hierarchy (`RateLimitError`, `InsufficientCreditsError`, …) |
| **Tests** | Manual against live FB | Recorded HTTP fixtures, Python 3.10–3.13 |
| **Surface area** | Page posts, group posts | 35+ Facebook endpoints + Instagram + Account |

## Pricing

| Tier | Calls / month | Price |
|---|---|---|
| **Free** | 200 | $0 |
| Pro | 1,500 | $4.99 |
| Ultra | 30,000 | $49 |
| Mega | 120,000 | $179 |
| Enterprise | Custom | [Contact us](https://socialapis.io/contact-us) |

One credit per successful call. Failed calls (4xx caused by bad input) don't consume credits.

## Other resources

- **Full SDK source + docs**: [SocialAPIsHub/socialapis-python](https://github.com/SocialAPIsHub/socialapis-python)
- **Instagram alternative** to [`arc298/instagram-scraper`](https://github.com/arc298/instagram-scraper): [SocialAPIsHub/instagram-scraper-python](https://github.com/SocialAPIsHub/instagram-scraper-python) (coming soon)
- **Hosted API docs**: [docs.socialapis.io](https://docs.socialapis.io)
- **Endpoint catalog (50+ endpoints)**: [socialapis.io/api-sources](https://socialapis.io/api-sources)
- **Status page**: [socialapis.io/status](https://socialapis.io/status)
- **Telegram (fastest support)**: [t.me/socialapis](https://t.me/socialapis)
- **Email**: [support@socialapis.io](mailto:support@socialapis.io)

## License

MIT — see [LICENSE](LICENSE).

The `socialapis` package this repo points at is also MIT-licensed. Both are open source; the hosted scraping API is the commercial layer.
