"""
Streamlit 주식 데이터 분석기 (실습용 기본 버전)
"""

# yfinance보다 먼저: 한글 Windows 경로 SSL 우회
import ssl_fix  # noqa: F401

from datetime import date, timedelta

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from stocks import STOCK_CATALOG

# 종목 비교 차트용 색상 팔레트
COMPARE_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


def korean_company_name(ticker: str, info: dict | None = None) -> str:
    """가능하면 한국어 회사명을 반환합니다. (예: 삼성전자)"""
    t = ticker.strip().upper()
    for item in STOCK_CATALOG:
        if item["ticker"].upper() == t:
            return item["name"]
    # 목록에 없으면 yfinance 이름 사용
    if info:
        return info.get("shortName") or info.get("longName") or ticker
    return ticker


def parse_tickers(raw: str) -> list[str]:
    """쉼표로 구분된 종목 코드를 정리해 목록으로 반환합니다."""
    parts = [p.strip().upper() for p in raw.replace("，", ",").split(",")]
    # 빈 항목 제거 + 순서 유지한 중복 제거
    seen: set[str] = set()
    tickers: list[str] = []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            tickers.append(p)
    return tickers


st.set_page_config(page_title="주식 데이터 분석기", page_icon="📈", layout="wide")

st.title("주식 데이터 분석기")
st.caption("yfinance로 주식 데이터를 조회합니다.")

# ============================================================
# 사이드바: 수익률 계산기
# ============================================================
with st.sidebar:
    st.header("수익률 계산기")
    st.caption("매수일 종가 기준으로 현재 가치·수익률을 계산합니다.")

    # 단일 종목 조회 결과가 있으면 기본 종목으로 사용
    default_calc_ticker = "005930.KS"
    if "stock_result" in st.session_state:
        # 메인 입력과 맞추기 위해 session에 ticker도 저장되어 있으면 사용
        default_calc_ticker = st.session_state.get("last_ticker", default_calc_ticker)

    calc_ticker = st.text_input(
        "종목 코드",
        value=default_calc_ticker,
        help="예: 005930.KS, AAPL",
        key="calc_ticker",
    ).strip()

    today = date.today()
    calc_buy_date = st.date_input(
        "매수 날짜",
        value=today - timedelta(days=90),
        max_value=today,
        key="calc_buy_date",
    )
    calc_amount = st.number_input(
        "매수 금액",
        min_value=0.0,
        value=1_000_000.0,
        step=10_000.0,
        format="%.0f",
        help="해당 통화 기준 투자 금액 (한국 종목=원, 미국=달러)",
        key="calc_amount",
    )

    if st.button("수익률 계산", type="primary", key="btn_calc"):
        if not calc_ticker:
            st.error("종목 코드를 입력해 주세요.")
        elif calc_amount <= 0:
            st.error("매수 금액을 0보다 크게 입력해 주세요.")
        else:
            with st.spinner("계산 중..."):
                try:
                    stock = yf.Ticker(calc_ticker)
                    # 매수일~오늘 (+여유일) 데이터 조회
                    end_date = today + timedelta(days=1)
                    hist = stock.history(start=calc_buy_date, end=end_date)
                    if hist.empty or "Close" not in hist.columns:
                        st.error("해당 기간 주가 데이터가 없습니다.")
                    else:
                        hist = hist.sort_index()
                        idx = hist.index
                        # 타임존 제거 후 날짜만 비교
                        if getattr(idx, "tz", None) is not None:
                            idx_dates = idx.tz_localize(None).date
                        else:
                            idx_dates = idx.date

                        buy_d = calc_buy_date
                        # 매수일 당일 또는 이후 첫 거래일
                        buy_pos = None
                        for i, d in enumerate(idx_dates):
                            if d >= buy_d:
                                buy_pos = i
                                break
                        if buy_pos is None:
                            st.error("매수 날짜 이후 거래 데이터가 없습니다.")
                        else:
                            buy_row = hist.iloc[buy_pos]
                            buy_close = float(buy_row["Close"])
                            actual_buy_date = idx_dates[buy_pos]
                            last_close = float(hist["Close"].iloc[-1])
                            last_date = idx_dates[-1]

                            if buy_close <= 0:
                                st.error("매수일 종가가 유효하지 않습니다.")
                            else:
                                shares = calc_amount / buy_close
                                current_value = shares * last_close
                                profit = current_value - calc_amount
                                return_pct = (profit / calc_amount) * 100.0
                                name = korean_company_name(calc_ticker, None)
                                if name == calc_ticker:
                                    try:
                                        name = korean_company_name(calc_ticker, stock.info)
                                    except Exception:
                                        name = calc_ticker

                                is_krw = calc_ticker.upper().endswith((".KS", ".KQ"))

                                def amt_fmt(v: float) -> str:
                                    if is_krw:
                                        return f"{v:,.0f}원"
                                    sign_char = "-" if v < 0 else ""
                                    return f"{sign_char}${abs(v):,.2f}"

                                color = "#2962FF" if profit >= 0 else "#EF5350"
                                sign = "+" if profit >= 0 else ""

                                note = ""
                                if actual_buy_date != buy_d:
                                    note = (
                                        f"<div style='font-size:0.85rem;color:#666;margin-top:0.35rem;'>"
                                        f"매수일이 휴장이라 <b>{actual_buy_date}</b> 종가를 사용했습니다."
                                        f"</div>"
                                    )

                                st.markdown(
                                    f"""
<div style="line-height:1.45; margin-top:0.5rem;">
  <div style="font-weight:700;">{name}</div>
  <div style="font-size:0.9rem; color:#555; margin-bottom:0.4rem;">{calc_ticker}</div>
  <div>매수가 : {amt_fmt(buy_close)} <span style="color:#888;">({actual_buy_date})</span></div>
  <div>현재가 : {amt_fmt(last_close)} <span style="color:#888;">({last_date})</span></div>
  <div>매수 금액 : {amt_fmt(calc_amount)}</div>
  <div>추정 수량 : {shares:,.4f}주</div>
  <hr style="margin:0.5rem 0; border:none; border-top:1px solid #ddd;"/>
  <div>현재 가치 : <b style="color:{color};">{amt_fmt(current_value)}</b></div>
  <div>손익 : <b style="color:{color};">{sign}{amt_fmt(profit)}</b></div>
  <div>수익률 : <b style="color:{color}; font-size:1.15rem;">{sign}{return_pct:.2f}%</b></div>
  {note}
</div>
""",
                                    unsafe_allow_html=True,
                                )
                except Exception as e:
                    st.error(f"계산에 실패했습니다: {e}")

# 기간 선택 (단일·비교 공통)
period_label = st.selectbox(
    "기간 선택",
    options=["1개월", "3개월", "6개월", "1년"],
)
period_map = {
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
}
period = period_map[period_label]

main_single, main_compare = st.tabs(["단일 종목", "종목 비교"])

# ============================================================
# 탭1: 단일 종목 (선 차트 / 캔들스틱)
# ============================================================
with main_single:
    ticker_input = st.text_input(
        "종목 코드",
        value="005930.KS",
        help="예: 005930.KS(삼성전자), AAPL(애플)",
        key="single_ticker",
    ).strip()

    if st.button("데이터 조회", type="primary", key="btn_single"):
        if not ticker_input:
            st.error("종목 코드를 입력해 주세요.")
            st.stop()

        with st.spinner("데이터를 불러오는 중..."):
            try:
                stock = yf.Ticker(ticker_input)
                info = stock.info
                history = stock.history(period=period)
            except Exception as e:
                st.error(f"데이터를 가져오지 못했습니다: {e}")
                st.stop()

        if history.empty:
            st.error("역사적 데이터가 비어 있습니다. 종목 코드를 확인해 주세요.")
            st.stop()

        company_name = korean_company_name(ticker_input, info)
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        if current_price is None:
            current_price = float(history["Close"].iloc[-1])

        change_pct = info.get("regularMarketChangePercent")
        if change_pct is None:
            prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
            if prev_close:
                change_pct = ((current_price - prev_close) / prev_close) * 100
            elif len(history) >= 2:
                prev = float(history["Close"].iloc[-2])
                change_pct = ((current_price - prev) / prev) * 100

        currency = info.get("currency", "USD")
        st.session_state["last_ticker"] = ticker_input.strip().upper()
        st.session_state["stock_result"] = {
            "history": history,
            "company_name": company_name,
            "current_price": current_price,
            "change_pct": change_pct,
            "currency": currency,
            "period_label": period_label,
        }

    if "stock_result" in st.session_state:
        result = st.session_state["stock_result"]
        history = result["history"]
        company_name = result["company_name"]
        current_price = result["current_price"]
        change_pct = result["change_pct"]
        currency = result["currency"]
        saved_period = result["period_label"]

        if currency == "KRW":
            price_text = f"{current_price:,.0f}원"
        else:
            price_text = f"${current_price:,.2f}"

        st.success("데이터 조회가 완료되었습니다.")

        change_text = f"{change_pct:+.2f}%" if change_pct is not None else "계산 불가"
        st.markdown(
            f"""
<div style="line-height:1.35; margin:0.15rem 0 0.35rem 0;">
  <div style="font-weight:700; margin-bottom:0.15rem;">{company_name}</div>
  <div style="display:flex; gap:1.5rem; flex-wrap:wrap; font-size:0.95rem;">
    <span>현재가 : {price_text}</span>
    <span>전일 대비 등락률 : {change_text}</span>
    <span>조회 기간 : {saved_period}</span>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        chart_df = history.sort_index(ascending=True).reset_index()
        chart_df["MA20"] = chart_df["Close"].rolling(window=20, min_periods=20).mean()
        chart_df["MA60"] = chart_df["Close"].rolling(window=60, min_periods=60).mean()
        has_ma20 = chart_df["MA20"].notna().any()
        has_ma60 = chart_df["MA60"].notna().any()

        y_tickformat = ",.0f" if currency == "KRW" else ",.2f"
        chart_layout = dict(
            xaxis_title="날짜",
            yaxis_title="가격",
            height=480,
            margin=dict(l=40, r=20, t=60, b=40),
            hovermode="x unified",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True, tickformat=y_tickformat),
        )

        ma_col1, ma_col2 = st.columns(2)
        with ma_col1:
            show_ma20 = st.checkbox(
                "MA20 표시 (주황)", value=True, disabled=not has_ma20, key="ma20"
            )
        with ma_col2:
            show_ma60 = st.checkbox(
                "MA60 표시 (초록)", value=True, disabled=not has_ma60, key="ma60"
            )
        if not has_ma20 or not has_ma60:
            missing = []
            if not has_ma20:
                missing.append("MA20")
            if not has_ma60:
                missing.append("MA60")
            st.caption(
                f"조회 기간 데이터가 부족해 {', '.join(missing)}을(를) 그릴 수 없습니다. "
                "기간을 늘려 다시 조회해 주세요."
            )

        def add_ma_traces(fig, row=None, col=None):
            """선택된 이동평균선을 차트에 추가합니다."""
            kwargs = {}
            if row is not None and col is not None:
                kwargs = {"row": row, "col": col}
            if show_ma20 and has_ma20:
                fig.add_trace(
                    go.Scatter(
                        x=chart_df["Date"],
                        y=chart_df["MA20"],
                        mode="lines",
                        name="MA20",
                        line=dict(color="#FF9800", width=1.8),
                        hovertemplate="날짜: %{x|%Y-%m-%d}<br>MA20: %{y:,.2f}<extra></extra>",
                    ),
                    **kwargs,
                )
            if show_ma60 and has_ma60:
                fig.add_trace(
                    go.Scatter(
                        x=chart_df["Date"],
                        y=chart_df["MA60"],
                        mode="lines",
                        name="MA60",
                        line=dict(color="#43A047", width=1.8),
                        hovertemplate="날짜: %{x|%Y-%m-%d}<br>MA60: %{y:,.2f}<extra></extra>",
                    ),
                    **kwargs,
                )

        tab_line, tab_candle = st.tabs(["선 차트", "캔들스틱 차트"])

        with tab_line:
            fig_line = go.Figure(
                data=[
                    go.Scatter(
                        x=chart_df["Date"],
                        y=chart_df["Close"],
                        mode="lines",
                        name="종가",
                        line=dict(color="#1f77b4", width=2),
                        hovertemplate="날짜: %{x|%Y-%m-%d}<br>가격: %{y:,.2f}<extra></extra>",
                    )
                ]
            )
            add_ma_traces(fig_line)
            fig_line.update_layout(
                title=f"{company_name} 주가 추이",
                **chart_layout,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            )
            st.plotly_chart(fig_line, use_container_width=True)

        with tab_candle:
            fig_candle = make_subplots(
                rows=2,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.04,
                row_heights=[0.72, 0.28],
                subplot_titles=(f"{company_name} 캔들스틱 차트", "거래량"),
            )

            fig_candle.add_trace(
                go.Candlestick(
                    x=chart_df["Date"],
                    open=chart_df["Open"],
                    high=chart_df["High"],
                    low=chart_df["Low"],
                    close=chart_df["Close"],
                    name="OHLC",
                    increasing_line_color="#2962FF",
                    increasing_fillcolor="#2962FF",
                    decreasing_line_color="#EF5350",
                    decreasing_fillcolor="#EF5350",
                ),
                row=1,
                col=1,
            )
            add_ma_traces(fig_candle, row=1, col=1)

            vol_avg = float(chart_df["Volume"].mean()) if len(chart_df) else 0.0
            is_up = chart_df["Close"] >= chart_df["Open"]
            is_high_vol = chart_df["Volume"] >= vol_avg
            vol_colors = []
            for up, high in zip(is_up, is_high_vol):
                if up and high:
                    vol_colors.append("rgba(41, 98, 255, 0.95)")
                elif up:
                    vol_colors.append("rgba(41, 98, 255, 0.45)")
                elif high:
                    vol_colors.append("rgba(239, 83, 80, 0.95)")
                else:
                    vol_colors.append("rgba(239, 83, 80, 0.45)")

            fig_candle.add_trace(
                go.Bar(
                    x=chart_df["Date"],
                    y=chart_df["Volume"],
                    name="거래량",
                    marker_color=vol_colors,
                    hovertemplate="날짜: %{x|%Y-%m-%d}<br>거래량: %{y:,.0f}<extra></extra>",
                ),
                row=2,
                col=1,
            )

            if vol_avg > 0:
                fig_candle.add_hline(
                    y=vol_avg,
                    line_dash="dot",
                    line_color="rgba(120,120,120,0.7)",
                    annotation_text="평균 거래량",
                    annotation_position="top left",
                    row=2,
                    col=1,
                )

            fig_candle.update_layout(
                height=620,
                margin=dict(l=40, r=20, t=60, b=40),
                hovermode="x unified",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                xaxis_rangeslider_visible=False,
            )
            fig_candle.update_xaxes(title_text="날짜", row=2, col=1, showgrid=True)
            fig_candle.update_yaxes(
                title_text="가격",
                tickformat=y_tickformat,
                showgrid=True,
                row=1,
                col=1,
            )
            fig_candle.update_yaxes(title_text="거래량", showgrid=True, row=2, col=1)
            st.plotly_chart(fig_candle, use_container_width=True)

        st.subheader("역사적 데이터")
        history_view = history.sort_index(ascending=False)
        history_kr = history_view.reset_index().rename(
            columns={
                "Date": "날짜",
                "Open": "시가",
                "High": "고가",
                "Low": "저가",
                "Close": "종가",
                "Volume": "거래량",
                "Dividends": "배당",
                "Stock Splits": "주식분할",
            }
        )

        price_cols = ["시가", "고가", "저가", "종가"]
        for col in price_cols:
            if col in history_kr.columns:
                if currency == "KRW":
                    history_kr[col] = history_kr[col].round(0).map(lambda x: f"{x:,.0f}")
                else:
                    history_kr[col] = history_kr[col].map(lambda x: f"{x:,.2f}")
        if "거래량" in history_kr.columns:
            history_kr["거래량"] = history_kr["거래량"].round(0).map(lambda x: f"{x:,.0f}")

        st.dataframe(history_kr, use_container_width=True)

# ============================================================
# 탭2: 종목 비교 (시작일=100 정규화 수익률)
# ============================================================
with main_compare:
    compare_input = st.text_input(
        "비교 종목 코드 (쉼표로 구분)",
        value="005930.KS, 000660.KS",
        help="예: 005930.KS, 000660.KS, AAPL",
        key="compare_tickers",
    )
    st.caption("시작일 종가=100으로 정규화해 상대 수익률을 비교합니다.")

    if st.button("비교 조회", type="primary", key="btn_compare"):
        tickers = parse_tickers(compare_input)
        if len(tickers) < 2:
            st.error("비교하려면 종목 코드를 2개 이상 입력해 주세요.")
            st.stop()

        series_list = []
        errors = []
        with st.spinner("여러 종목 데이터를 불러오는 중..."):
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period=period)
                    if hist.empty or "Close" not in hist.columns:
                        errors.append(f"{ticker}: 데이터가 비어 있습니다.")
                        continue
                    # 타임존 제거 후 날짜만 맞춰 비교
                    closes = hist["Close"].copy()
                    closes.index = closes.index.tz_localize(None) if closes.index.tz else closes.index
                    closes = closes.sort_index()
                    base = float(closes.iloc[0])
                    if base == 0:
                        errors.append(f"{ticker}: 시작 종가가 0입니다.")
                        continue
                    normalized = (closes / base) * 100.0
                    name = korean_company_name(ticker, None)
                    # 카탈로그에 없으면 yfinance에서 한 번 더 시도
                    if name == ticker:
                        try:
                            name = korean_company_name(ticker, stock.info)
                        except Exception:
                            name = ticker
                    series_list.append(
                        {
                            "ticker": ticker,
                            "name": name,
                            "normalized": normalized,
                            "return_pct": float(normalized.iloc[-1] - 100.0),
                        }
                    )
                except Exception as e:
                    errors.append(f"{ticker}: {e}")

        if not series_list:
            st.error("비교할 수 있는 종목 데이터가 없습니다.")
            for msg in errors:
                st.warning(msg)
            st.stop()

        st.session_state["compare_result"] = {
            "series_list": series_list,
            "errors": errors,
            "period_label": period_label,
        }

    if "compare_result" in st.session_state:
        cmp = st.session_state["compare_result"]
        series_list = cmp["series_list"]
        errors = cmp["errors"]
        saved_period = cmp["period_label"]

        st.success("종목 비교 조회가 완료되었습니다.")
        if errors:
            for msg in errors:
                st.warning(msg)

        # 정규화 비교 차트
        fig_cmp = go.Figure()
        for i, item in enumerate(series_list):
            color = COMPARE_COLORS[i % len(COMPARE_COLORS)]
            s = item["normalized"]
            fig_cmp.add_trace(
                go.Scatter(
                    x=s.index,
                    y=s.values,
                    mode="lines",
                    name=item["name"],
                    line=dict(color=color, width=2),
                    hovertemplate=(
                        f"{item['name']}<br>"
                        "날짜: %{x|%Y-%m-%d}<br>"
                        "지수: %{y:.2f}<extra></extra>"
                    ),
                )
            )

        # 기준선 100
        fig_cmp.add_hline(
            y=100,
            line_dash="dot",
            line_color="rgba(120,120,120,0.7)",
            annotation_text="시작=100",
            annotation_position="top left",
        )

        fig_cmp.update_layout(
            title=f"종목 비교 (시작일=100, {saved_period})",
            xaxis_title="날짜",
            yaxis_title="정규화 지수 (시작=100)",
            height=520,
            margin=dict(l=40, r=20, t=60, b=40),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

        # 기간 수익률 요약 표
        summary_rows = [
            {
                "종목명": item["name"],
                "종목코드": item["ticker"],
                "기간 수익률(%)": f"{item['return_pct']:+.2f}",
            }
            for item in series_list
        ]
        st.subheader("기간 수익률 요약")
        st.dataframe(summary_rows, use_container_width=True, hide_index=True)
