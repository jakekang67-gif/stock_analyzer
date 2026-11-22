"""종목 검색 커스텀 컴포넌트 (한글 입력 즉시 필터링)."""

from __future__ import annotations

import os
from typing import Any

import streamlit.components.v1 as components

_DIR = os.path.dirname(os.path.abspath(__file__))
_FRONTEND = os.path.join(_DIR, "frontend")

_stock_search = components.declare_component(
    "stock_search",
    path=_FRONTEND,
)


def stock_search_widget(
    catalog: list[dict],
    *,
    default_query: str = "",
    default_ticker: str | None = None,
    key: str | None = None,
) -> dict[str, Any] | None:
    """
    이름/코드 입력 즉시 '시작 일치' 종목을 보여주고,
    사용자가 고른 종목을 dict로 반환합니다.
    """
    slim = [
        {
            "name": c["name"],
            "ticker": c["ticker"],
            "aliases": c.get("aliases", []),
        }
        for c in catalog
    ]
    return _stock_search(
        catalog=slim,
        default_query=default_query,
        default_ticker=default_ticker,
        key=key,
        default=None,
    )
