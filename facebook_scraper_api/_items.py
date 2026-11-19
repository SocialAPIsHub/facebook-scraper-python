"""Find the records in an answer and flatten them for CSV.

Endpoints wrap their list under different keys (``posts``, ``items``,
``videos``, …), so instead of a per-endpoint path we take the longest list of
objects in the answer, outside our own ``meta`` / ``message`` envelope. The
same rule reads live answers in the SocialAPIs Google Sheets add-on.
"""

from __future__ import annotations

import json
from typing import Any

from ._paging import ENVELOPE_KEYS


def _best_list(node: Any, depth: int) -> list[dict[str, Any]] | None:
    if depth > 3:
        return None
    if isinstance(node, list):
        if node and all(isinstance(x, dict) for x in node):
            return node
        return None
    if not isinstance(node, dict):
        return None
    best: list[dict[str, Any]] | None = None
    for key, value in node.items():
        if key in ENVELOPE_KEYS:
            continue
        found = _best_list(value, depth + 1)
        if found is not None and (best is None or len(found) > len(best)):
            best = found
    return best


def items_of(body: Any) -> list[dict[str, Any]]:
    """The records of one answer (posts, comments, videos…), or ``[]``."""
    return _best_list(body, 0) or []


def record_of(body: Any) -> dict[str, Any]:
    """A single-record answer without our envelope (and its ``"0"`` / ``data`` wrapper)."""
    if not isinstance(body, dict):
        return {}
    for key in ("0", "data"):
        inner = body.get(key)
        if isinstance(inner, dict):
            return inner
    return {k: v for k, v in body.items() if k not in ENVELOPE_KEYS}


def _cell(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list) and all(x is None or not isinstance(x, (dict, list)) for x in value):
        return ", ".join(str(x) for x in value if x is not None)
    return json.dumps(value, ensure_ascii=False)


def flatten(record: dict[str, Any], prefix: str = "", depth: int = 0) -> dict[str, Any]:
    """``{"a": 1, "b": {"c": 2}}`` → ``{"a": 1, "b.c": 2}`` (two levels; deeper parts stay JSON)."""
    out: dict[str, Any] = {}
    for key, value in record.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict) and depth < 2:
            out.update(flatten(value, name, depth + 1))
        else:
            out[name] = _cell(value)
    return out
