"""
상승 추세를 찾는 실시간 주식 데이터 분석기
- yfinance로 주가 조회
- 이동평균(MA)으로 상승 추세 판별
- Plotly 차트 + Streamlit UI (PC·모바일 대응)
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from stocks import (
    format_stock_label,
    resolve_many,
    resolve_to_ticker,
    search_stocks,
)


# ---------------------------------------------------------------------------
# 페이지 설정
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="주식 데이터 분석기",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# PC·모바일 공통 반응형 스타일 + 하단 Streamlit UI 숨김
st.markdown(
    """
    <style>
    /* 기본 여백 축소 */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1100px;
    }

    h1 {
        font-size: 1.6rem !important;
        line-height: 1.35 !important;
        margin-bottom: 0.35rem !important;
    }

    [data-testid="stMetricValue"] { font-size: 1.15rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem !important; }
    [data-testid="stDataFrame"] { overflow-x: auto; }

    /* Streamlit 기본 메뉴·푸터·장식 숨김 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    .stDeployButton { display: none !important; }
    .stAppDeployButton { display: none !important; }

    /* Streamlit Cloud 하단 배지 / Manage app 계열 */
    div[class*="viewerBadge"],
    a[class*="viewerBadge"],
    a[href*="streamlit.io"],
    a[href*="share.streamlit.io"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    /* 모바일: 설정(사이드바) 가로 꽉 채우기 */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.8rem;
            padding-left: 0.6rem;
            padding-right: 0.6rem;
        }
        h1 { font-size: 1.25rem !important; }
        [data-testid="stMetricValue"] { font-size: 1rem !important; }

        section[data-testid="stSidebar"] {
            width: 100vw !important;
            min-width: 100vw !important;
            max-width: 100vw !important;
            transform: translateX(0) !important;
        }
        section[data-testid="stSidebar"] > div {
            width: 100% !important;
            max-width: 100vw !important;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        /* 사이드바 열렸을 때 본문이 비치지 않도록 */
        [data-testid="stSidebarContent"] {
            width: 100% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📈 상승 추세를 찾는 주식 데이터 분석기")
st.caption("야후 파이낸스 데이터 · 이동평균(MA) 기반 기술적 분석 · PC·모바일 지원")


# ---------------------------------------------------------------------------
# 헬퍼 함수
# ---------------------------------------------------------------------------
def currency_label(code: str) -> str:
    """통화 코드를 한국어 표기로 변환합니다."""
    mapping = {
        "USD": "달러",
        "KRW": "원",
        "JPY": "엔",
        "EUR": "유로",
        "GBP": "파운드",
        "CNY": "위안",
        "HKD": "홍콩달러",
    }
    return mapping.get(code, code)


def format_money(value: float, currency: str) -> str:
    """금액을 통화에 맞게 표시합니다. (원화는 소수점 없음)"""
    label = currency_label(currency)
    if currency == "KRW":
        return f"{value:,.0f} {label}"
    return f"{value:,.2f} {label}"


@st.cache_data(ttl=300)
def fetch_history(ticker: str, period: str) -> pd.DataFrame:
    """종목의 기간별 시세 데이터를 가져옵니다."""
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    if df.empty:
        return df
    return df.reset_index()


@st.cache_data(ttl=300)
def fetch_info(ticker: str) -> dict:
    """종목 기본 정보(현재가, 등락률 등)를 가져옵니다."""
    return yf.Ticker(ticker).info


def add_moving_averages(df: pd.DataFrame, short: int = 20, long: int = 60) -> pd.DataFrame:
    """단기·장기 이동평균을 추가합니다."""
    df = df.copy()
    df[f"MA{short}"] = df["Close"].rolling(window=short).mean()
    df[f"MA{long}"] = df["Close"].rolling(window=long).mean()
    return df


def detect_uptrend(df: pd.DataFrame, short: int = 20, long: int = 60) -> dict:
    """이동평균 기반 상승 추세 판별."""
    ma_s = f"MA{short}"
    ma_l = f"MA{long}"

    if len(df) < long or df[ma_s].isna().iloc[-1] or df[ma_l].isna().iloc[-1]:
        return {
            "is_uptrend": False,
            "label": "데이터 부족",
            "detail": f"이동평균 계산에 최소 {long}거래일이 필요합니다.",
            "golden_cross": False,
        }

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    price_above_ma = latest["Close"] > latest[ma_s]
    ma_aligned = latest[ma_s] > latest[ma_l]
    ma_rising = latest[ma_s] > prev[ma_s]

    golden_cross = False
    lookback = min(5, len(df) - 1)
    for i in range(-lookback, 0):
        curr, before = df.iloc[i], df.iloc[i - 1]
        if pd.notna(before[ma_s]) and pd.notna(before[ma_l]):
            if before[ma_s] <= before[ma_l] and curr[ma_s] > curr[ma_l]:
                golden_cross = True
                break

    is_uptrend = ma_aligned and price_above_ma

    if golden_cross and is_uptrend:
        label, detail = "🚀 강한 상승 추세", "정배열 + 최근 골든크로스 발생"
    elif is_uptrend and ma_rising:
        label, detail = (
            "📈 상승 추세",
            "단기 이동평균 > 장기 이동평균, 종가가 단기 이동평균 위, 이동평균 우상향",
        )
    elif is_uptrend:
        label, detail = "📈 상승 추세 (약함)", "정배열이지만 단기 이동평균 상승세는 둔화"
    elif ma_aligned:
        label, detail = "⚠️ 혼조", "정배열이지만 종가가 단기 이동평균 아래"
    else:
        label, detail = "📉 하락/횡보 추세", "단기 이동평균이 장기 이동평균 아래 (역배열)"

    return {
        "is_uptrend": is_uptrend,
        "label": label,
        "detail": detail,
        "golden_cross": golden_cross,
    }


def chart_layout_opts(height: int) -> dict:
    """PC·모바일 공통 차트 레이아웃 옵션."""
    return dict(
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11),
        ),
        margin=dict(l=48, r=16, t=56, b=36),
        hovermode="x unified",
        dragmode="pan",
        font=dict(family="Malgun Gothic, Apple SD Gothic Neo, sans-serif"),
    )


def build_price_chart(
    df: pd.DataFrame, ticker: str, short: int, long: int, height: int = 520
) -> go.Figure:
    """종가 + 이동평균 + 거래량 차트."""
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{ticker} 주가와 이동평균", "거래량"),
    )
    fig.add_trace(
        go.Scatter(x=df["Date"], y=df["Close"], name="종가", line=dict(color="#1f77b4", width=2)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[f"MA{short}"],
            name=f"단기 이동평균({short}일)",
            line=dict(color="#ff7f0e", width=1.5, dash="dot"),
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[f"MA{long}"],
            name=f"장기 이동평균({long}일)",
            line=dict(color="#2ca02c", width=1.5, dash="dash"),
        ),
        row=1, col=1,
    )
    colors = ["#ef5350" if c < o else "#26a69a" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(
        go.Bar(x=df["Date"], y=df["Volume"], name="거래량", marker_color=colors),
        row=2, col=1,
    )
    fig.update_layout(**chart_layout_opts(height))
    fig.update_yaxes(title_text="가격", row=1, col=1)
    fig.update_yaxes(title_text="거래량", row=2, col=1)
    fig.update_xaxes(title_text="날짜", row=2, col=1)
    return fig


def build_compare_chart(data: dict[str, pd.DataFrame], height: int = 380) -> go.Figure:
    """여러 종목의 정규화(시작=100) 수익률 비교 차트."""
    fig = go.Figure()
    for ticker, df in data.items():
        if df.empty:
            continue
        normalized = (df["Close"] / df["Close"].iloc[0]) * 100
        fig.add_trace(go.Scatter(x=df["Date"], y=normalized, name=ticker, mode="lines"))
    fig.update_layout(
        **chart_layout_opts(height),
        title="종목 비교 (시작점 = 100)",
        yaxis_title="정규화 지수",
        xaxis_title="날짜",
    )
    return fig


def calc_profit(df: pd.DataFrame, amount: float) -> dict | None:
    """과거 첫 거래일 매수 → 현재 가정 수익률."""
    if df.empty or len(df) < 2:
        return None
    buy_price = float(df["Close"].iloc[0])
    sell_price = float(df["Close"].iloc[-1])
    shares = amount / buy_price
    profit = shares * (sell_price - buy_price)
    return_rate = ((sell_price - buy_price) / buy_price) * 100
    return {
        "buy_date": df["Date"].iloc[0],
        "buy_price": buy_price,
        "sell_price": sell_price,
        "shares": shares,
        "profit": profit,
        "return_rate": return_rate,
        "final_value": amount + profit,
    }


PLOTLY_CONFIG = {
    "responsive": True,
    "displayModeBar": True,
    "scrollZoom": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {"format": "png", "filename": "주식차트"},
}


# ---------------------------------------------------------------------------
# 사이드바 — 입력
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 설정")
    st.caption("📱 모바일: 왼쪽 위 ≫ 메뉴에서 설정을 열 수 있습니다.")

    st.subheader("종목 검색")
    stock_query = st.text_input(
        "이름 또는 코드",
        value=st.session_state.get("stock_query", "삼성"),
        placeholder="예: 삼 / 애플 / AAPL / 005930",
        help="한 글자만 입력해도 자동으로 후보가 나타납니다.",
        key="stock_query_input",
    ).strip()

    selected_ticker = None
    selected_label = None
    matches = search_stocks(stock_query) if stock_query else []

    if stock_query:
        if matches:
            labels = [format_stock_label(m) for m in matches]
            # 이전에 고른 값이 있으면 유지
            default_idx = 0
            prev_label = st.session_state.get("selected_stock_label")
            if prev_label in labels:
                default_idx = labels.index(prev_label)
            selected_label = st.selectbox(
                "검색 결과",
                options=labels,
                index=default_idx,
                help="원하는 종목을 선택하세요.",
            )
            selected_ticker = matches[labels.index(selected_label)]["ticker"]
            st.caption(f"선택됨: **{selected_label}**")
        else:
            # 목록에 없으면 입력을 티커로 시도
            selected_ticker = resolve_to_ticker(stock_query)
            st.info(f"목록에 없어 코드 `{selected_ticker}` 로 조회합니다.")
    else:
        st.caption("한 글자 이상 입력하면 종목이 검색됩니다.")

    period = st.selectbox(
        "조회 기간",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
        format_func=lambda x: {
            "1mo": "1개월",
            "3mo": "3개월",
            "6mo": "6개월",
            "1y": "1년",
            "2y": "2년",
            "5y": "5년",
        }[x],
    )

    st.subheader("이동평균 기간")
    col_ma1, col_ma2 = st.columns(2)
    with col_ma1:
        ma_short = st.number_input("단기(일)", min_value=5, max_value=50, value=20, step=1)
    with col_ma2:
        ma_long = st.number_input("장기(일)", min_value=20, max_value=200, value=60, step=5)

    if ma_short >= ma_long:
        st.warning("단기 이동평균은 장기 이동평균보다 작아야 합니다.")

    chart_size = st.radio(
        "화면 / 차트 크기",
        options=["자동(권장)", "모바일", "PC"],
        index=0,
        horizontal=True,
        help="모바일에서 차트가 크면 '모바일'을 선택하세요.",
    )

    st.divider()
    compare_raw = st.text_input(
        "비교 종목 (쉼표로 구분)",
        value="애플, 테슬라",
        help="이름 또는 코드 가능. 예: 마이크로소프트, TSLA, 000660.KS",
    )
    invest_amount = st.number_input(
        "가상 투자 금액",
        min_value=100.0,
        value=10000.0,
        step=100.0,
        help="선택한 기간 시작일에 매수했다고 가정합니다.",
    )

    analyze = st.button("분석하기", type="primary", use_container_width=True)


# 차트 높이
if chart_size == "모바일":
    price_chart_h, compare_chart_h = 420, 300
elif chart_size == "PC":
    price_chart_h, compare_chart_h = 560, 420
else:
    price_chart_h, compare_chart_h = 480, 340


# ---------------------------------------------------------------------------
# 메인 영역
# ---------------------------------------------------------------------------
if not analyze and "last_ticker" not in st.session_state:
    st.info("왼쪽 **설정**에서 종목을 검색·선택한 뒤 **분석하기**를 눌러 주세요. (모바일은 왼쪽 위 ≫ 메뉴)")
    st.markdown(
        """
        ### 사용 예시
        | 시장 | 검색어 예 | 코드 |
        |------|-----------|------|
        | 한국 | `삼` / `삼성전자` | `005930.KS` |
        | 한국 | `하이닉스` | `000660.KS` |
        | 미국 | `애` / `애플` / `AAPL` | `AAPL` |
        | 미국 | `테슬라` / `TSLA` | `TSLA` |
        """
    )
    st.stop()

if analyze:
    if not selected_ticker:
        st.error("종목을 검색하고 선택한 뒤 다시 **분석하기**를 눌러 주세요.")
        st.stop()
    st.session_state["last_ticker"] = selected_ticker
    st.session_state["last_stock_label"] = selected_label or selected_ticker
    st.session_state["selected_stock_label"] = selected_label
    st.session_state["last_period"] = period
    st.session_state["last_ma_short"] = ma_short
    st.session_state["last_ma_long"] = ma_long
    st.session_state["last_compare"] = compare_raw
    st.session_state["last_amount"] = invest_amount
    st.session_state["last_chart_size"] = chart_size

ticker = st.session_state.get("last_ticker", selected_ticker)
period = st.session_state.get("last_period", period)
ma_short = int(st.session_state.get("last_ma_short", ma_short))
ma_long = int(st.session_state.get("last_ma_long", ma_long))
compare_raw = st.session_state.get("last_compare", compare_raw)
invest_amount = float(st.session_state.get("last_amount", invest_amount))
chart_size = st.session_state.get("last_chart_size", chart_size)
display_label = st.session_state.get("last_stock_label", ticker)

if chart_size == "모바일":
    price_chart_h, compare_chart_h = 420, 300
elif chart_size == "PC":
    price_chart_h, compare_chart_h = 560, 420
else:
    price_chart_h, compare_chart_h = 480, 340

if not ticker:
    st.error("종목이 선택되지 않았습니다.")
    st.stop()

if ma_short >= ma_long:
    st.error("단기 이동평균은 장기 이동평균보다 작아야 합니다. 설정에서 수정해 주세요.")
    st.stop()

with st.spinner(f"{display_label} 데이터를 불러오는 중..."):
    try:
        df = fetch_history(ticker, period)
        info = fetch_info(ticker)
    except Exception as e:
        st.error(f"데이터를 가져오지 못했습니다: {e}")
        st.stop()

if df.empty:
    st.error(f"`{ticker}` 데이터를 찾을 수 없습니다. 종목 이름/코드를 확인해 주세요.")
    st.stop()

df = add_moving_averages(df, ma_short, ma_long)
trend = detect_uptrend(df, ma_short, ma_long)

name = info.get("shortName") or info.get("longName") or display_label
currency = info.get("currency", "USD")
current = info.get("currentPrice") or info.get("regularMarketPrice") or float(df["Close"].iloc[-1])
prev_close = info.get("previousClose") or (
    float(df["Close"].iloc[-2]) if len(df) > 1 else current
)
change = current - prev_close
change_pct = (change / prev_close * 100) if prev_close else 0.0

st.subheader(f"{name} (`{ticker}`)")

row1 = st.columns(2)
row2 = st.columns(2)
row1[0].metric("현재가", format_money(current, currency), f"{change:+.2f} ({change_pct:+.2f}%)")
row1[1].metric("기간 시작가", format_money(float(df["Close"].iloc[0]), currency))
row2[0].metric("기간 최고가", format_money(float(df["High"].max()), currency))
row2[1].metric("기간 최저가", format_money(float(df["Low"].min()), currency))

if trend["is_uptrend"]:
    st.success(f"**{trend['label']}** — {trend['detail']}")
else:
    st.warning(f"**{trend['label']}** — {trend['detail']}")

if trend["golden_cross"]:
    st.info("✨ 최근 5거래일 내 **골든크로스**(단기 이동평균이 장기 이동평균을 상향 돌파)가 감지되었습니다.")

st.plotly_chart(
    build_price_chart(df, ticker, ma_short, ma_long, height=price_chart_h),
    use_container_width=True,
    config=PLOTLY_CONFIG,
)

st.subheader("💰 가상 투자 수익률")
result = calc_profit(df, invest_amount)
if result:
    r1, r2 = st.columns(2)
    r1.metric("매수가 (기간 시작)", format_money(result["buy_price"], currency))
    r2.metric("현재가 (기간 끝)", format_money(result["sell_price"], currency))
    st.metric(
        "수익 / 수익률",
        format_money(result["profit"], currency),
        f"{result['return_rate']:+.2f}%",
    )
    st.caption(
        f"{result['buy_date'].strftime('%Y-%m-%d')}에 "
        f"{format_money(invest_amount, currency)} 매수 → "
        f"평가금 {format_money(result['final_value'], currency)}"
    )

st.subheader("📊 종목 비교")
compare_tickers = [t for t in resolve_many(compare_raw) if t != ticker]
all_tickers = [ticker] + compare_tickers

compare_data: dict[str, pd.DataFrame] = {ticker: df}
failed = []
for t in all_tickers[1:]:
    try:
        cdf = fetch_history(t, period)
        if cdf.empty:
            failed.append(t)
        else:
            compare_data[t] = cdf
    except Exception:
        failed.append(t)

if len(compare_data) > 1:
    st.plotly_chart(
        build_compare_chart(compare_data, height=compare_chart_h),
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )
    rows = []
    for t, cdf in compare_data.items():
        cdf_ma = add_moving_averages(cdf, ma_short, ma_long)
        t_trend = detect_uptrend(cdf_ma, ma_short, ma_long)
        ret = ((cdf["Close"].iloc[-1] / cdf["Close"].iloc[0]) - 1) * 100
        rows.append(
            {
                "종목": t,
                "기간 수익률(%)": round(ret, 2),
                "추세": t_trend["label"],
                "골든크로스": "있음" if t_trend["golden_cross"] else "없음",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.caption("비교할 다른 종목을 설정에 입력하면 정규화 차트가 표시됩니다.")

if failed:
    st.caption(f"불러오지 못한 종목: {', '.join(failed)}")

st.divider()
st.caption(
    "데이터 출처: 야후 파이낸스(yfinance) · 투자 권유가 아니며, 참고용 분석 도구입니다."
)
