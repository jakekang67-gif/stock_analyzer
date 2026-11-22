"""
자주 쓰는 주식 종목 목록과 이름/코드 검색 유틸
"""

from __future__ import annotations

# name: 표시용 한글/영문 이름
# ticker: yfinance 심볼
# aliases: 추가 검색어
STOCK_CATALOG: list[dict] = [
    # ---- 한국 ----
    {"name": "삼성전자", "ticker": "005930.KS", "aliases": ["삼성", "samsung", "005930"]},
    {"name": "SK하이닉스", "ticker": "000660.KS", "aliases": ["하이닉스", "hynix", "000660"]},
    {"name": "현대차", "ticker": "005380.KS", "aliases": ["현대자동차", "hyundai", "005380"]},
    {"name": "기아", "ticker": "000270.KS", "aliases": ["kia", "000270"]},
    {"name": "NAVER", "ticker": "035420.KS", "aliases": ["네이버", "naver", "035420"]},
    {"name": "카카오", "ticker": "035720.KS", "aliases": ["kakao", "035720"]},
    {"name": "LG에너지솔루션", "ticker": "373220.KS", "aliases": ["엘지엔솔", "lg엔솔", "373220"]},
    {"name": "삼성바이오로직스", "ticker": "207940.KS", "aliases": ["삼바", "207940"]},
    {"name": "셀트리온", "ticker": "068270.KS", "aliases": ["068270"]},
    {"name": "KB금융", "ticker": "105560.KS", "aliases": ["국민은행", "105560"]},
    {"name": "신한지주", "ticker": "055550.KS", "aliases": ["신한", "055550"]},
    {"name": "POSCO홀딩스", "ticker": "005490.KS", "aliases": ["포스코", "posco", "005490"]},
    {"name": "삼성SDI", "ticker": "006400.KS", "aliases": ["삼에스디아이", "006400"]},
    {"name": "LG화학", "ticker": "051910.KS", "aliases": ["엘지화학", "051910"]},
    {"name": "카카오뱅크", "ticker": "323410.KS", "aliases": ["카뱅", "323410"]},
    {"name": "크래프톤", "ticker": "259960.KS", "aliases": ["krafton", "259960"]},
    {"name": "한화에어로스페이스", "ticker": "012450.KS", "aliases": ["한화에어로", "012450"]},
    {"name": "두산에너빌리티", "ticker": "034020.KS", "aliases": ["두산에너", "034020"]},
    {"name": "삼성물산", "ticker": "028260.KS", "aliases": ["028260"]},
    {"name": "SK텔레콤", "ticker": "017670.KS", "aliases": ["skt", "017670"]},
    {"name": "KT", "ticker": "030200.KS", "aliases": ["케이티", "030200"]},
    {"name": "LG전자", "ticker": "066570.KS", "aliases": ["엘지전자", "066570"]},
    {"name": "현대모비스", "ticker": "012330.KS", "aliases": ["모비스", "012330"]},
    {"name": "아모레퍼시픽", "ticker": "090430.KS", "aliases": ["아모레", "090430"]},
    {"name": "코스피200 ETF", "ticker": "069500.KS", "aliases": ["kodex200", "069500"]},
    # ---- 미국 ----
    {"name": "애플", "ticker": "AAPL", "aliases": ["apple", "aapl"]},
    {"name": "마이크로소프트", "ticker": "MSFT", "aliases": ["microsoft", "msft"]},
    {"name": "구글", "ticker": "GOOGL", "aliases": ["알파벳", "alphabet", "google", "googl", "goog"]},
    {"name": "아마존", "ticker": "AMZN", "aliases": ["amazon", "amzn"]},
    {"name": "엔비디아", "ticker": "NVDA", "aliases": ["nvidia", "nvda"]},
    {"name": "테슬라", "ticker": "TSLA", "aliases": ["tesla", "tsla"]},
    {"name": "메타", "ticker": "META", "aliases": ["페이스북", "facebook", "meta", "fb"]},
    {"name": "넷플릭스", "ticker": "NFLX", "aliases": ["netflix", "nflx"]},
    {"name": "인텔", "ticker": "INTC", "aliases": ["intel", "intc"]},
    {"name": "AMD", "ticker": "AMD", "aliases": ["amd"]},
    {"name": "코카콜라", "ticker": "KO", "aliases": ["coca cola", "coke", "ko"]},
    {"name": "디즈니", "ticker": "DIS", "aliases": ["disney", "dis"]},
    {"name": "JP모건", "ticker": "JPM", "aliases": ["jpmorgan", "jpm"]},
    {"name": "비자", "ticker": "V", "aliases": ["visa"]},
    {"name": "유니티", "ticker": "U", "aliases": ["unity"]},
    {"name": "팔란티어", "ticker": "PLTR", "aliases": ["palantir", "pltr"]},
    {"name": "코인베이스", "ticker": "COIN", "aliases": ["coinbase", "coin"]},
]


def _norm(text: str) -> str:
    return text.strip().lower().replace(" ", "")


def format_stock_label(item: dict) -> str:
    """선택 목록에 표시할 문구."""
    return f"{item['name']} ({item['ticker']})"


def search_stocks(query: str, limit: int = 20) -> list[dict]:
    """
    한 글자 이상이면 이름·코드·별칭에서 부분 일치 검색.
    결과가 여러 개면 이름 시작 일치 → 티커 시작 일치 → 그 외 순으로 정렬.
    """
    q = _norm(query)
    if not q:
        return []

    scored: list[tuple[int, dict]] = []
    for item in STOCK_CATALOG:
        name_n = _norm(item["name"])
        ticker_n = _norm(item["ticker"])
        alias_n = [_norm(a) for a in item.get("aliases", [])]
        haystacks = [name_n, ticker_n, *alias_n]

        if not any(q in h for h in haystacks):
            continue

        # 점수가 낮을수록 상위
        if name_n.startswith(q) or ticker_n.startswith(q):
            score = 0
        elif any(a.startswith(q) for a in alias_n):
            score = 1
        else:
            score = 2
        scored.append((score, item))

    # 인기 종목을 같은 점수대에서 앞으로
    popular_rank = {
        "005930.KS": 0,  # 삼성전자
        "000660.KS": 1,
        "AAPL": 2,
        "TSLA": 3,
        "NVDA": 4,
        "MSFT": 5,
        "GOOGL": 6,
        "035720.KS": 7,  # 카카오
        "035420.KS": 8,  # 네이버
    }
    scored.sort(
        key=lambda x: (
            x[0],
            popular_rank.get(x[1]["ticker"], 100),
            x[1]["name"],
        )
    )
    # 티커 기준 중복 제거
    seen: set[str] = set()
    result: list[dict] = []
    for _, item in scored:
        if item["ticker"] in seen:
            continue
        seen.add(item["ticker"])
        result.append(item)
        if len(result) >= limit:
            break
    return result


def resolve_to_ticker(text: str) -> str | None:
    """
    이름 또는 코드를 yfinance 티커로 변환.
    목록에 없으면 입력값을 티커 후보로 정규화해 반환.
    """
    raw = text.strip()
    if not raw:
        return None

    matches = search_stocks(raw, limit=5)
    # 완전 일치 우선
    q = _norm(raw)
    for item in matches:
        if (
            _norm(item["name"]) == q
            or _norm(item["ticker"]) == q
            or q in [_norm(a) for a in item.get("aliases", [])]
        ):
            return item["ticker"]

    if matches:
        return matches[0]["ticker"]

    # 목록 밖: 한국 숫자 코드면 .KS 보정 시도
    cleaned = raw.upper().replace(" ", "")
    if cleaned.isdigit() and len(cleaned) == 6:
        return f"{cleaned}.KS"
    return cleaned


def resolve_many(raw: str) -> list[str]:
    """쉼표로 구분된 여러 종목을 티커 리스트로 변환."""
    tickers: list[str] = []
    for part in raw.split(","):
        t = resolve_to_ticker(part)
        if t and t not in tickers:
            tickers.append(t)
    return tickers
