# facebook-scraper-api

Public Facebook data from Python: Page details, Page and group posts, reels, videos, comments and search. Functions in the style of the old `facebook-scraper` (`get_posts(account, pages=...)`), but the data comes from a hosted API, so nothing breaks when Facebook changes its pages: **no login, no cookies, no browser, no proxies**.

Powered by [SocialAPIs](https://socialapis.io). **[Get a free API key](https://socialapis.io/auth/signup)**: 200 calls/month, no card.

```bash
pip install facebook-scraper-api
export SOCIALAPIS_TOKEN=your_key
```

```python
from facebook_scraper_api import get_page_info, get_posts, get_comments

page = get_page_info("nasa")
print(page["title"], page["followers_count"])

for post in get_posts("nasa", pages=2, limit=9):   # 2 calls, 9 posts each
    print(post)

for comment in get_comments("https://www.facebook.com/nasa/posts/...", pages=1):
    print(comment)
```

Or call `set_api_token("...")` first instead of the environment variable.

| Function | What it returns |
|---|---|
| `get_page_info(account)` | A Page's details: name, followers, likes, category, contact, links |
| `get_posts(account, pages=1, limit=None, after=None, before=None)` | A Page's posts, newest first |
| `get_group_posts(group, pages=1, ...)` / `get_posts(group=...)` | A public group's posts |
| `get_group_info(group)` | A public group's details |
| `get_reels(account, pages=1)` / `get_videos(account, pages=1)` | A Page's reels / videos |
| `get_post(post_url, extended=False)` | One post's details |
| `get_comments(post_url, pages=1)` | Comments on a post or reel |
| `search_posts(query, pages=1)` / `search_pages(query, pages=1)` | Keyword search |

Listings are generators: they follow the API's `end_cursor` and stop after `pages` calls or when there are no more results. `account` is a Page URL or username; `group` is a group URL or id. For several keys or a custom connection, use `FacebookScraperAPI(api_token=...)`, which has the same methods.

## Command line

```bash
facebook-scraper-api page nasa
facebook-scraper-api posts nasa --pages 3 --limit 9 --out nasa.csv
facebook-scraper-api group-posts https://www.facebook.com/groups/123 --format jsonl
facebook-scraper-api comments https://www.facebook.com/nasa/posts/123 --pages 2
```

CSV columns are the fields of the records (nested fields as `reactions.total`).

## Costs

Most calls cost 1 credit. Page and group posts cost round(limit ÷ 3) credits per call (limit 3-9, default 3). Failed calls (4xx / 5xx) are not charged. [Pricing](https://socialapis.io/pricing).

## Links

- [Endpoint reference](https://socialapis.io/api-sources/facebook-page-posts) · [Free Facebook follower count tool](https://socialapis.io/tools/facebook-follower-count)
- Source and migration guide from `facebook-scraper`: [github.com/SocialAPIsHub/facebook-scraper-python](https://github.com/SocialAPIsHub/facebook-scraper-python)
- Full SDK (Instagram, Marketplace, Ads Library, async): [`socialapis-sdk`](https://pypi.org/project/socialapis-sdk/) · Meta Ads Library only: [`facebook-ads-library-api`](https://pypi.org/project/facebook-ads-library-api/)

Public data only. You are responsible for how you use it, including personal data rules (GDPR) where they apply. MIT license.
