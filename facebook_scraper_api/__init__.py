"""Facebook scraper API for Python: public Pages, posts, groups, reels, comments and search.

Works like the old ``facebook-scraper`` functions (``get_posts(account, pages=...)``)
but the data comes from a hosted API, so nothing breaks when Facebook changes
its pages: no login, no cookies, no browser, no proxies. Powered by
SocialAPIs (https://socialapis.io).

Quick start::

    from facebook_scraper_api import get_page_info, get_posts, set_api_token

    set_api_token("YOUR_API_TOKEN")  # or set SOCIALAPIS_TOKEN

    print(get_page_info("nasa")["followers_count"])
    for post in get_posts("nasa", pages=2):
        print(post)

Free API key (200 calls/month, no card): https://socialapis.io/auth/signup
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from typing import Any

from socialapis import Facebook

from ._items import flatten, items_of, record_of
from ._paging import next_cursor, paginate

__version__ = "0.1.0"

__all__ = [
    "FacebookScraperAPI",
    "__version__",
    "flatten",
    "get_comments",
    "get_group_info",
    "get_group_posts",
    "get_page_info",
    "get_post",
    "get_posts",
    "get_reels",
    "get_videos",
    "items_of",
    "next_cursor",
    "search_pages",
    "search_posts",
    "set_api_token",
]


class FacebookScraperAPI:
    """All calls of this package on one client (one API key, one connection pool).

    Every API call costs credits (1 per call for most; Page / group posts
    cost round(limit / 3)). ``pages`` caps how many calls a listing makes.
    """

    def __init__(self, api_token: str | None = None, *, client: Facebook | None = None) -> None:
        if client is None:
            token = api_token or os.environ.get("SOCIALAPIS_TOKEN")
            if not token:
                raise ValueError(
                    "Call set_api_token(...) or set SOCIALAPIS_TOKEN. Get a free key at "
                    "https://socialapis.io/auth/signup (200 calls/month, no card)."
                )
            client = Facebook(api_token=token)
        self._fb = client

    def __enter__(self) -> FacebookScraperAPI:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._fb.close()

    def _items(self, call: Callable[..., dict[str, Any]], pages: int, **params: Any) -> Iterator[dict[str, Any]]:
        for body in paginate(lambda cursor: call(end_cursor=cursor, **params), pages):
            yield from items_of(body)

    # ---- single records ----------------------------------------------------

    def get_page_info(self, account: str, **params: Any) -> dict[str, Any]:
        """A Page's public details: name, followers, likes, category, contact, links."""
        return self._fb.get_page_info(account, **params).model_dump(exclude_none=True)

    def get_group_info(self, group: str, **params: Any) -> dict[str, Any]:
        """A public group's details: name, members, privacy, description."""
        return self._fb.get_group_details(group, **params).model_dump(exclude_none=True)

    def get_post(self, post_url: str, *, extended: bool = False, **params: Any) -> dict[str, Any]:
        """One post's details (``extended=True`` adds views, video URLs, music)."""
        call = self._fb.get_post_details_extended if extended else self._fb.get_post_details
        return record_of(call(post_url, **params))

    # ---- listings ----------------------------------------------------------

    def get_posts(
        self,
        account: str | None = None,
        *,
        group: str | None = None,
        pages: int = 1,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        **params: Any,
    ) -> Iterator[dict[str, Any]]:
        """Recent posts of a Page (``account``) or a public ``group``, newest first.

        ``limit`` is posts per call (3-9, default 3; cost round(limit / 3)
        credits per call). ``after`` / ``before`` are ISO 8601 timestamps.
        """
        if (account is None) == (group is None):
            raise ValueError("give a Page (account) or a group, not both")
        if limit is not None and not 3 <= limit <= 9:
            raise ValueError("limit is posts per call, from 3 to 9")
        target = account if account is not None else group
        call = self._fb.get_page_posts if account is not None else self._fb.get_group_posts
        yield from self._items(
            lambda **kw: call(target, **kw),  # type: ignore[arg-type]
            pages,
            limit=limit,
            after_time=after,
            before_time=before,
            **params,
        )

    def get_reels(self, account: str, *, pages: int = 1, **params: Any) -> Iterator[dict[str, Any]]:
        """A Page's reels."""
        yield from self._items(lambda **kw: self._fb.get_page_reels(account, **kw), pages, **params)

    def get_videos(self, account: str, *, pages: int = 1, **params: Any) -> Iterator[dict[str, Any]]:
        """A Page's long-form videos."""
        yield from self._items(lambda **kw: self._fb.get_page_videos(account, **kw), pages, **params)

    def get_comments(self, post_url: str, *, pages: int = 1, **params: Any) -> Iterator[dict[str, Any]]:
        """Top-level comments on a post or reel."""
        yield from self._items(lambda **kw: self._fb.get_post_comments(post_url, **kw), pages, **params)

    def search_posts(self, query: str, *, pages: int = 1, **params: Any) -> Iterator[dict[str, Any]]:
        """Public posts matching a keyword."""
        yield from self._items(lambda **kw: self._fb.search_posts(query, **kw), pages, **params)

    def search_pages(self, query: str, *, pages: int = 1, **params: Any) -> Iterator[dict[str, Any]]:
        """Pages matching a keyword."""
        yield from self._items(lambda **kw: self._fb.search_pages(query, **kw), pages, **params)


# ---------------------------------------------------------------------------
# Module-level functions, facebook-scraper style. They share one client,
# created on first use from set_api_token() or SOCIALAPIS_TOKEN.
# ---------------------------------------------------------------------------

_default: FacebookScraperAPI | None = None


def set_api_token(api_token: str) -> None:
    """Use this API key for the module-level functions."""
    global _default
    if _default is not None:
        _default.close()
    _default = FacebookScraperAPI(api_token)


def _client() -> FacebookScraperAPI:
    global _default
    if _default is None:
        _default = FacebookScraperAPI()
    return _default


def get_page_info(account: str, **params: Any) -> dict[str, Any]:
    """A Page's public details. See :meth:`FacebookScraperAPI.get_page_info`."""
    return _client().get_page_info(account, **params)


def get_group_info(group: str, **params: Any) -> dict[str, Any]:
    """A public group's details. See :meth:`FacebookScraperAPI.get_group_info`."""
    return _client().get_group_info(group, **params)


def get_post(post_url: str, **params: Any) -> dict[str, Any]:
    """One post's details. See :meth:`FacebookScraperAPI.get_post`."""
    return _client().get_post(post_url, **params)


def get_posts(account: str | None = None, **params: Any) -> Iterator[dict[str, Any]]:
    """Posts of a Page or group. See :meth:`FacebookScraperAPI.get_posts`."""
    return _client().get_posts(account, **params)


def get_group_posts(group: str, **params: Any) -> Iterator[dict[str, Any]]:
    """Posts of a public group."""
    return _client().get_posts(group=group, **params)


def get_reels(account: str, **params: Any) -> Iterator[dict[str, Any]]:
    """A Page's reels."""
    return _client().get_reels(account, **params)


def get_videos(account: str, **params: Any) -> Iterator[dict[str, Any]]:
    """A Page's long-form videos."""
    return _client().get_videos(account, **params)


def get_comments(post_url: str, **params: Any) -> Iterator[dict[str, Any]]:
    """Comments on a post or reel."""
    return _client().get_comments(post_url, **params)


def search_posts(query: str, **params: Any) -> Iterator[dict[str, Any]]:
    """Public posts matching a keyword."""
    return _client().search_posts(query, **params)


def search_pages(query: str, **params: Any) -> Iterator[dict[str, Any]]:
    """Pages matching a keyword."""
    return _client().search_pages(query, **params)
