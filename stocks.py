"""
자주 쓰는 주식 종목 목록과 이름/코드 검색 유틸
"""

from __future__ import annotations

# name: 표시용 한글/영문 이름
# ticker: yfinance 심볼 (.KS=코스피, .KQ=코스닥)
# aliases: 추가 검색어
STOCK_CATALOG: list[dict] = [
    # ---- 삼성 그룹 (삼* 검색용) ----
    {"name": "삼성전자", "ticker": "005930.KS", "aliases": ["삼성", "samsung", "005930"]},
    {"name": "삼성전자우", "ticker": "005935.KS", "aliases": ["삼성우선주", "005935"]},
    {"name": "삼성SDI", "ticker": "006400.KS", "aliases": ["삼에스디아이", "006400"]},
    {"name": "삼성SDI우", "ticker": "006405.KS", "aliases": ["006405"]},
    {"name": "삼성물산", "ticker": "028260.KS", "aliases": ["028260"]},
    {"name": "삼성물산우B", "ticker": "02826K.KS", "aliases": ["02826K"]},
    {"name": "삼성바이오로직스", "ticker": "207940.KS", "aliases": ["삼바", "207940"]},
    {"name": "삼성전기", "ticker": "009150.KS", "aliases": ["샘전", "009150"]},
    {"name": "삼성전기우", "ticker": "009155.KS", "aliases": ["009155"]},
    {"name": "삼성생명", "ticker": "032830.KS", "aliases": ["032830"]},
    {"name": "삼성화재", "ticker": "000810.KS", "aliases": ["삼화", "000810"]},
    {"name": "삼성화재우", "ticker": "000815.KS", "aliases": ["000815"]},
    {"name": "삼성에스디에스", "ticker": "018260.KS", "aliases": ["삼성SDS", "삼성sds", "018260"]},
    {"name": "삼성중공업", "ticker": "010140.KS", "aliases": ["삼중", "010140"]},
    {"name": "삼성증권", "ticker": "016360.KS", "aliases": ["016360"]},
    {"name": "삼성카드", "ticker": "029780.KS", "aliases": ["029780"]},
    {"name": "삼성E&A", "ticker": "028050.KS", "aliases": ["삼성엔지니어링", "삼엔", "028050"]},
    {"name": "삼성출판사", "ticker": "068290.KQ", "aliases": ["068290"]},
    {"name": "삼양식품", "ticker": "003230.KS", "aliases": ["003230"]},
    {"name": "삼양홀딩스", "ticker": "000070.KS", "aliases": ["000070"]},
    {"name": "삼양사", "ticker": "145990.KS", "aliases": ["145990"]},
    {"name": "삼천리", "ticker": "004690.KS", "aliases": ["004690"]},
    {"name": "삼천당제약", "ticker": "000250.KQ", "aliases": ["000250"]},
    {"name": "삼성제약", "ticker": "001360.KS", "aliases": ["001360"]},
    {"name": "삼표시멘트", "ticker": "038500.KQ", "aliases": ["038500"]},
    {"name": "삼화페인트", "ticker": "000390.KS", "aliases": ["000390"]},
    {"name": "삼화콘덴서", "ticker": "001820.KS", "aliases": ["001820"]},
    {"name": "삼익THK", "ticker": "004380.KS", "aliases": ["삼익", "004380"]},
    {"name": "삼일제약", "ticker": "000520.KS", "aliases": ["000520"]},
    {"name": "삼진제약", "ticker": "023000.KS", "aliases": ["023000"]},
    {"name": "삼호개발", "ticker": "010960.KS", "aliases": ["010960"]},
    {"name": "삼영", "ticker": "003720.KS", "aliases": ["003720"]},
    {"name": "삼익악기", "ticker": "002450.KS", "aliases": ["002450"]},
    {"name": "삼부토건", "ticker": "001470.KS", "aliases": ["001470"]},
    {"name": "삼성스팩", "ticker": "448730.KQ", "aliases": ["448730"]},

    # ---- 국내 대형주 · 주요 종목 ----
    {"name": "SK하이닉스", "ticker": "000660.KS", "aliases": ["하이닉스", "hynix", "000660"]},
    {"name": "현대차", "ticker": "005380.KS", "aliases": ["현대자동차", "hyundai", "005380"]},
    {"name": "현대차우", "ticker": "005385.KS", "aliases": ["005385"]},
    {"name": "기아", "ticker": "000270.KS", "aliases": ["kia", "000270"]},
    {"name": "NAVER", "ticker": "035420.KS", "aliases": ["네이버", "naver", "035420"]},
    {"name": "카카오", "ticker": "035720.KS", "aliases": ["kakao", "035720"]},
    {"name": "LG에너지솔루션", "ticker": "373220.KS", "aliases": ["엘지엔솔", "lg엔솔", "373220"]},
    {"name": "셀트리온", "ticker": "068270.KS", "aliases": ["068270"]},
    {"name": "KB금융", "ticker": "105560.KS", "aliases": ["국민은행", "105560"]},
    {"name": "신한지주", "ticker": "055550.KS", "aliases": ["신한", "055550"]},
    {"name": "하나금융지주", "ticker": "086790.KS", "aliases": ["하나금융", "086790"]},
    {"name": "우리금융지주", "ticker": "316140.KS", "aliases": ["우리금융", "316140"]},
    {"name": "POSCO홀딩스", "ticker": "005490.KS", "aliases": ["포스코", "posco", "005490"]},
    {"name": "포스코퓨처엠", "ticker": "003670.KS", "aliases": ["포스코케미칼", "003670"]},
    {"name": "LG화학", "ticker": "051910.KS", "aliases": ["엘지화학", "051910"]},
    {"name": "LG전자", "ticker": "066570.KS", "aliases": ["엘지전자", "066570"]},
    {"name": "LG", "ticker": "003550.KS", "aliases": ["엘지", "003550"]},
    {"name": "카카오뱅크", "ticker": "323410.KS", "aliases": ["카뱅", "323410"]},
    {"name": "카카오페이", "ticker": "377300.KS", "aliases": ["카페", "377300"]},
    {"name": "크래프톤", "ticker": "259960.KS", "aliases": ["krafton", "259960"]},
    {"name": "한화에어로스페이스", "ticker": "012450.KS", "aliases": ["한화에어로", "012450"]},
    {"name": "한화오션", "ticker": "042660.KS", "aliases": ["대우조선해양", "042660"]},
    {"name": "한화솔루션", "ticker": "009830.KS", "aliases": ["009830"]},
    {"name": "두산에너빌리티", "ticker": "034020.KS", "aliases": ["두산에너", "034020"]},
    {"name": "두산", "ticker": "000150.KS", "aliases": ["000150"]},
    {"name": "SK텔레콤", "ticker": "017670.KS", "aliases": ["skt", "017670"]},
    {"name": "SK스퀘어", "ticker": "402340.KS", "aliases": ["402340"]},
    {"name": "SK이노베이션", "ticker": "096770.KS", "aliases": ["에스케이이노", "096770"]},
    {"name": "SK", "ticker": "034730.KS", "aliases": ["에스케이", "034730"]},
    {"name": "KT", "ticker": "030200.KS", "aliases": ["케이티", "030200"]},
    {"name": "KT&G", "ticker": "033780.KS", "aliases": ["케이티앤지", "담배인삼", "033780"]},
    {"name": "현대모비스", "ticker": "012330.KS", "aliases": ["모비스", "012330"]},
    {"name": "현대건설", "ticker": "000720.KS", "aliases": ["000720"]},
    {"name": "현대글로비스", "ticker": "086280.KS", "aliases": ["글로비스", "086280"]},
    {"name": "현대제철", "ticker": "004020.KS", "aliases": ["004020"]},
    {"name": "HL만도", "ticker": "204320.KS", "aliases": ["만도", "204320"]},
    {"name": "아모레퍼시픽", "ticker": "090430.KS", "aliases": ["아모레", "090430"]},
    {"name": "아모레G", "ticker": "002790.KS", "aliases": ["002790"]},
    {"name": "LG생활건강", "ticker": "051900.KS", "aliases": ["엘지생활건강", "051900"]},
    {"name": "대한항공", "ticker": "003490.KS", "aliases": ["003490"]},
    {"name": "한진칼", "ticker": "180640.KS", "aliases": ["180640"]},
    {"name": "아시아나항공", "ticker": "020560.KS", "aliases": ["020560"]},
    {"name": "한국전력", "ticker": "015760.KS", "aliases": ["한전", "015760"]},
    {"name": "한국가스공사", "ticker": "036460.KS", "aliases": ["가스공사", "036460"]},
    {"name": "S-Oil", "ticker": "010950.KS", "aliases": ["에쓰오일", "010950"]},
    {"name": "고려아연", "ticker": "010130.KS", "aliases": ["010130"]},
    {"name": "LG디스플레이", "ticker": "034220.KS", "aliases": ["엘지디스플레이", "034220"]},
    {"name": "넷마블", "ticker": "251270.KS", "aliases": ["251270"]},
    {"name": "엔씨소프트", "ticker": "036570.KS", "aliases": ["엔씨", "ncsoft", "036570"]},
    {"name": "하이브", "ticker": "352820.KS", "aliases": ["hive", "352820"]},
    {"name": "JYP Ent.", "ticker": "035900.KQ", "aliases": ["제이와이피", "jyp", "035900"]},
    {"name": "에스엠", "ticker": "041510.KQ", "aliases": ["SM", "041510"]},
    {"name": "와이지엔터테인먼트", "ticker": "122870.KQ", "aliases": ["YG", "와이지", "122870"]},
    {"name": "쿠팡", "ticker": "CPNG", "aliases": ["coupang", "cpng"]},
    {"name": "유한양행", "ticker": "000100.KS", "aliases": ["000100"]},
    {"name": "한미약품", "ticker": "128940.KS", "aliases": ["128940"]},
    {"name": "녹십자", "ticker": "006280.KS", "aliases": ["006280"]},
    {"name": "SK바이오팜", "ticker": "326030.KS", "aliases": ["326030"]},
    {"name": "알테오젠", "ticker": "196170.KQ", "aliases": ["196170"]},
    {"name": "에코프로", "ticker": "086520.KQ", "aliases": ["086520"]},
    {"name": "에코프로비엠", "ticker": "247540.KQ", "aliases": ["에코비엠", "247540"]},
    {"name": "엘앤에프", "ticker": "066970.KS", "aliases": ["066970"]},
    {"name": "LG이노텍", "ticker": "011070.KS", "aliases": ["엘지이노텍", "011070"]},
    {"name": "한온시스템", "ticker": "018880.KS", "aliases": ["018880"]},
    {"name": "HMM", "ticker": "011200.KS", "aliases": ["현대상선", "011200"]},
    {"name": "팬오션", "ticker": "028670.KS", "aliases": ["028670"]},
    {"name": "KODEX 200", "ticker": "069500.KS", "aliases": ["코스피200", "kodex200", "069500"]},
    {"name": "TIGER 미국S&P500", "ticker": "360750.KS", "aliases": ["타이거스앤피", "360750"]},
    {"name": "KODEX 레버리지", "ticker": "122630.KS", "aliases": ["122630"]},
    {"name": "KODEX 인버스", "ticker": "114800.KS", "aliases": ["114800"]},

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
    {"name": "브로드컴", "ticker": "AVGO", "aliases": ["broadcom", "avgo"]},
    {"name": "코카콜라", "ticker": "KO", "aliases": ["coca cola", "coke", "ko"]},
    {"name": "디즈니", "ticker": "DIS", "aliases": ["disney", "dis"]},
    {"name": "JP모건", "ticker": "JPM", "aliases": ["jpmorgan", "jpm"]},
    {"name": "비자", "ticker": "V", "aliases": ["visa"]},
    {"name": "유니티", "ticker": "U", "aliases": ["unity"]},
    {"name": "팔란티어", "ticker": "PLTR", "aliases": ["palantir", "pltr"]},
    {"name": "코인베이스", "ticker": "COIN", "aliases": ["coinbase", "coin"]},
    {"name": "버크셔해서웨이", "ticker": "BRK-B", "aliases": ["버크셔", "berkshire", "brk"]},
]


def _norm(text: str) -> str:
    return text.strip().lower().replace(" ", "")


def format_stock_label(item: dict) -> str:
    """선택 목록에 표시할 문구."""
    return f"{item['name']} ({item['ticker']})"


def search_stocks(query: str, limit: int = 50) -> list[dict]:
    """
    한 글자 이상이면 이름·코드·별칭이 검색어로 '시작하는' 종목만 반환.
    예: '삼' → 삼성전자, 삼성전기, 삼성생명 ...
    """
    q = _norm(query)
    if not q:
        return []

    scored: list[tuple[int, dict]] = []
    for item in STOCK_CATALOG:
        name_n = _norm(item["name"])
        ticker_n = _norm(item["ticker"])
        alias_n = [_norm(a) for a in item.get("aliases", [])]

        name_hit = name_n.startswith(q)
        ticker_hit = ticker_n.startswith(q)
        alias_hit = any(a.startswith(q) for a in alias_n)
        if not (name_hit or ticker_hit or alias_hit):
            continue

        if name_hit:
            score = 0
        elif ticker_hit:
            score = 1
        else:
            score = 2
        scored.append((score, item))

    popular_rank = {
        "005930.KS": 0,
        "000660.KS": 1,
        "AAPL": 2,
        "TSLA": 3,
        "NVDA": 4,
        "MSFT": 5,
        "GOOGL": 6,
        "035720.KS": 7,
        "035420.KS": 8,
        "006400.KS": 9,
        "207940.KS": 10,
        "009150.KS": 11,
    }
    scored.sort(
        key=lambda x: (
            x[0],
            popular_rank.get(x[1]["ticker"], 100),
            x[1]["name"],
        )
    )
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
    """이름 또는 코드를 yfinance 티커로 변환."""
    raw = text.strip()
    if not raw:
        return None

    matches = search_stocks(raw, limit=8)
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
