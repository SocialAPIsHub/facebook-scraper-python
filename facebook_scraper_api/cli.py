"""Command line: Facebook Pages, posts, groups, reels and comments to CSV or JSON lines.

    facebook-scraper-api page nasa
    facebook-scraper-api posts nasa --pages 3 --limit 9 --out nasa.csv
    facebook-scraper-api group-posts https://www.facebook.com/groups/123 --format jsonl
    facebook-scraper-api comments https://www.facebook.com/nasa/posts/123 --pages 2

The API key comes from --token or the SOCIALAPIS_TOKEN environment variable.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections.abc import Iterable
from typing import Any, TextIO

from socialapis import SocialAPIsError

from . import FacebookScraperAPI, __version__
from ._items import flatten

LISTINGS = {
    "posts": ("Page posts", "Page URL or username"),
    "group-posts": ("public group posts", "group URL or id"),
    "reels": ("Page reels", "Page URL or username"),
    "videos": ("Page videos", "Page URL or username"),
    "comments": ("comments on a post or reel", "post URL"),
    "search-posts": ("public posts matching a keyword", "keyword"),
    "search-pages": ("Pages matching a keyword", "keyword"),
}


def write_rows(records: Iterable[dict[str, Any]], fmt: str, out: TextIO) -> int:
    """CSV (headers = every field seen, in order) or one JSON object per line."""
    records = list(records)
    if fmt == "jsonl":
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
        return len(records)
    flat = [flatten(r) for r in records]
    headers: list[str] = []
    for row in flat:
        headers.extend(k for k in row if k not in headers)
    writer = csv.DictWriter(out, fieldnames=headers or ["(no results)"])
    writer.writeheader()
    writer.writerows(flat)
    return len(flat)


def _listing(api: FacebookScraperAPI, args: argparse.Namespace) -> Iterable[dict[str, Any]]:
    common: dict[str, Any] = {"pages": args.pages}
    if args.command in ("posts", "group-posts"):
        common.update(limit=args.limit, after=args.after, before=args.before)
        if args.command == "posts":
            return api.get_posts(args.target, **common)
        return api.get_posts(group=args.target, **common)
    calls = {
        "reels": api.get_reels,
        "videos": api.get_videos,
        "comments": api.get_comments,
        "search-posts": api.search_posts,
        "search-pages": api.search_pages,
    }
    return calls[args.command](args.target, **common)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="facebook-scraper-api",
        description="Public Facebook data (Pages, posts, groups, reels, comments) without a login or browser.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--token", help="SocialAPIs API key (default: $SOCIALAPIS_TOKEN)")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("page", "group"):
        p = sub.add_parser(name, help=f"a {name}'s details (JSON)")
        p.add_argument("target", help="URL, username or id")

    for name, (help_text, target_help) in LISTINGS.items():
        p = sub.add_parser(name, help=help_text)
        p.add_argument("target", help=target_help)
        p.add_argument("--pages", type=int, default=1, help="API calls to make (default 1)")
        if name in ("posts", "group-posts"):
            p.add_argument("--limit", type=int, help="posts per call, 3-9 (cost round(limit / 3) credits per call)")
            p.add_argument("--after", help="only posts after this time (ISO 8601)")
            p.add_argument("--before", help="only posts before this time (ISO 8601)")
        p.add_argument("--format", choices=["csv", "jsonl"], default="csv")
        p.add_argument("--out", help="file to write (default: standard output)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with FacebookScraperAPI(api_token=args.token) as api:
            if args.command in ("page", "group"):
                info = api.get_page_info(args.target) if args.command == "page" else api.get_group_info(args.target)
                print(json.dumps(info, indent=2, ensure_ascii=False))
                return 0
            records = _listing(api, args)
            if args.out:
                with open(args.out, "w", newline="", encoding="utf-8") as fh:
                    count = write_rows(records, args.format, fh)
                print(f"{count} rows written to {args.out}", file=sys.stderr)
            else:
                write_rows(records, args.format, sys.stdout)
    except (SocialAPIsError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
