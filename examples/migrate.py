"""Side-by-side migration example: kevinzg/facebook-scraper → socialapis.

The shape stays familiar — `FacebookScraper` is an exact alias of
`socialapis.Facebook`, so changing your import is the entire migration.

Run this:
    1. Sign up free at https://socialapis.io/auth/signup
    2. export SOCIALAPIS_TOKEN="<paste your token from the dashboard>"
    3. pip install socialapis-sdk
    4. python examples/migrate.py
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# BEFORE — kevinzg/facebook-scraper (abandoned, breaks on every Meta change)
# ---------------------------------------------------------------------------
#
# from facebook_scraper import get_page_info, get_posts
#
# page = get_page_info("EngenSA")
# print(page["name"], page["likes"])
#
# for post in get_posts("EngenSA", pages=5):
#     print(post["time"], post["text"][:80])

# ---------------------------------------------------------------------------
# AFTER — socialapis (hosted, typed, maintained)
# ---------------------------------------------------------------------------

from socialapis import FacebookScraper, InsufficientCreditsError, RateLimitError


def main() -> None:
    token = os.environ.get("SOCIALAPIS_TOKEN")
    if not token:
        raise SystemExit(
            "Set SOCIALAPIS_TOKEN — sign up free at "
            "https://socialapis.io/auth/signup"
        )

    # FacebookScraper is an alias of socialapis.Facebook. Same class,
    # same methods, identical behaviour — just a name that mirrors
    # kevinzg's import surface for greppable migrations.
    with FacebookScraper(api_token=token) as fb:
        try:
            page = fb.get_page_info("EngenSA")
        except RateLimitError as exc:
            raise SystemExit(
                f"Rate-limited. Wait {exc.retry_after_seconds}s and retry."
            ) from exc
        except InsufficientCreditsError:
            raise SystemExit(
                "Out of credits. Upgrade at https://socialapis.io/pricing"
            ) from None

        # Same fields kevinzg returned, but typed — page.name not page["name"]
        print(f"Page: {page.name}")
        print(f"  Category: {page.category}")
        print(f"  Likes:    {page.likes:,}" if page.likes else "  Likes:    n/a")
        print(f"  Verified: {page.verified}")

        # kevinzg's `for post in get_posts(...)` equivalent —
        # paginate via cursors instead of `pages=N`.
        result = fb.get_page_posts("EngenSA")
        for post in result.get("posts", [])[:5]:
            timestamp = post.get("time") or post.get("published_at", "?")
            text = post.get("text") or post.get("message", "")
            print(f"  [{timestamp}] {text[:80]}")


if __name__ == "__main__":
    main()
