from __future__ import annotations

import csv
import io
from typing import Any

import pytest

from facebook_scraper_api import FacebookScraperAPI, flatten, items_of
from facebook_scraper_api.cli import write_rows

POST_A = {"post_id": "1", "message": "Hello", "reactions": {"total": 5, "like": 4}}
POST_B = {"post_id": "2", "message": "World", "attachments": [{"type": "photo"}]}


def answer(posts: list[dict[str, Any]], cursor: str | None) -> dict[str, Any]:
    return {
        "message": "ok",
        "meta": {"statusCode": 200, "creditsCharged": 1},
        "data": {"posts": posts, "page_info": {"end_cursor": cursor, "has_next_page": cursor is not None}},
    }


class FakeFacebook:
    def __init__(self, answers: list[dict[str, Any]]) -> None:
        self.answers = answers
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def _answer(self, name: str, target: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((name, target, kwargs))
        return self.answers[len(self.calls) - 1]

    def get_page_posts(self, page: str, **kwargs: Any) -> dict[str, Any]:
        return self._answer("page_posts", page, kwargs)

    def get_group_posts(self, group: str, **kwargs: Any) -> dict[str, Any]:
        return self._answer("group_posts", group, kwargs)

    def get_post_comments(self, post: str, **kwargs: Any) -> dict[str, Any]:
        return self._answer("comments", post, kwargs)

    def close(self) -> None:
        pass


def test_posts_follow_the_cursor() -> None:
    fb = FakeFacebook([answer([POST_A], "c1"), answer([POST_B], None)])
    api = FacebookScraperAPI(client=fb)  # type: ignore[arg-type]
    posts = list(api.get_posts("nasa", pages=5, limit=9))
    assert [p["post_id"] for p in posts] == ["1", "2"]
    assert fb.calls[0] == (
        "page_posts",
        "nasa",
        {"end_cursor": None, "limit": 9, "after_time": None, "before_time": None},
    )
    assert fb.calls[1][2]["end_cursor"] == "c1"


def test_pages_is_a_ceiling() -> None:
    fb = FakeFacebook([answer([POST_A], "c1"), answer([POST_B], "c2")])
    list(FacebookScraperAPI(client=fb).get_posts("nasa", pages=1))  # type: ignore[arg-type]
    assert len(fb.calls) == 1


def test_group_posts() -> None:
    fb = FakeFacebook([answer([POST_A], None)])
    list(FacebookScraperAPI(client=fb).get_posts(group="123"))  # type: ignore[arg-type]
    assert fb.calls[0][:2] == ("group_posts", "123")


def test_post_arguments_are_checked() -> None:
    api = FacebookScraperAPI(client=FakeFacebook([]))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="not both"):
        list(api.get_posts("nasa", group="123"))
    with pytest.raises(ValueError, match="not both"):
        list(api.get_posts())
    with pytest.raises(ValueError, match="3 to 9"):
        list(api.get_posts("nasa", limit=20))


def test_items_of_takes_the_longest_list_outside_the_envelope() -> None:
    body = {
        "meta": {"warnings": [{"a": 1}, {"b": 2}, {"c": 3}]},
        "data": {"items": [POST_A, POST_B], "page_info": {}},
    }
    assert items_of(body) == [POST_A, POST_B]
    assert items_of({"data": [POST_A]}) == [POST_A]
    assert items_of({"data": {"posts": []}}) == []


def test_flatten_and_csv() -> None:
    assert flatten(POST_A) == {"post_id": "1", "message": "Hello", "reactions.total": 5, "reactions.like": 4}
    out = io.StringIO()
    assert write_rows([POST_A, POST_B], "csv", out) == 2
    rows = list(csv.DictReader(io.StringIO(out.getvalue())))
    assert rows[1]["attachments"] == '[{"type": "photo"}]'
    assert rows[0]["reactions.total"] == "5"


def test_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SOCIALAPIS_TOKEN", raising=False)
    with pytest.raises(ValueError, match="SOCIALAPIS_TOKEN"):
        FacebookScraperAPI()
