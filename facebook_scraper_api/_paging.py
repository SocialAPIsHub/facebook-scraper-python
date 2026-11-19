"""Cursor handling shared by every paginated call.

The API returns its next-page cursor as ``end_cursor`` (usually inside a
``page_info`` block next to ``has_next_page``). Where exactly it sits differs
by endpoint, so we look for it instead of hard-coding a path, and stop as soon
as there is no cursor, ``has_next_page`` is false, or a cursor repeats.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

# Our own envelope around every answer: never data, never a cursor.
ENVELOPE_KEYS = ("meta", "message")

_STOP = object()


def _find_cursor(node: Any, depth: int) -> Any:
    if depth > 4 or not isinstance(node, dict):
        return None
    info = node.get("page_info")
    if isinstance(info, dict):
        if info.get("has_next_page") is False:
            return _STOP
        cursor = info.get("end_cursor")
        if isinstance(cursor, str) and cursor:
            return cursor
    cursor = node.get("end_cursor")
    if isinstance(cursor, str) and cursor:
        return cursor
    for key, value in node.items():
        if key in ENVELOPE_KEYS:
            continue
        found = _find_cursor(value, depth + 1)
        if found is not None:
            return found
    return None


def next_cursor(body: Any) -> str | None:
    """The cursor for the next page, or None when there is no next page."""
    found = _find_cursor(body, 0)
    return found if isinstance(found, str) else None


def paginate(
    fetch: Callable[[str | None], dict[str, Any]],
    pages: int,
) -> Iterator[dict[str, Any]]:
    """Call ``fetch(cursor)`` up to ``pages`` times, yielding each answer.

    Every call is a billed API call, so ``pages`` is a hard ceiling.
    """
    if pages < 1:
        raise ValueError("pages must be 1 or more")
    cursor: str | None = None
    seen: set[str] = set()
    for _ in range(pages):
        body = fetch(cursor)
        yield body
        cursor = next_cursor(body)
        if cursor is None or cursor in seen:
            return
        seen.add(cursor)
