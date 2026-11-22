"""
yfinance로 삼성전자(005930.KS) 데이터를 가져오는 테스트 스크립트
"""

import ssl_fix  # noqa: F401

import yfinance as yf


def main() -> None:
    ticker_symbol = "005930.KS"
    stock = yf.Ticker(ticker_symbol)

    info = stock.info
    company_name = info.get("longName") or info.get("shortName") or ticker_symbol
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    change_pct = info.get("regularMarketChangePercent")
    if change_pct is None:
        previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        if current_price is not None and previous_close:
            change_pct = ((current_price - previous_close) / previous_close) * 100

    print("=== 삼성전자 주식 정보 ===")
    print(f"회사명: {company_name}")
    if current_price is not None:
        print(f"현재가: {current_price:,.0f}원")
    else:
        print("현재가: 없음")
    if change_pct is not None:
        print(f"전일 대비 등락률: {change_pct:+.2f}%")
    else:
        print("전일 대비 등락률: 계산 불가")

    print("\n최근 1개월 데이터 (처음 5개 행):")
    history = stock.history(period="1mo")
    if history.empty:
        print("역사적 데이터를 가져오지 못했습니다.")
    else:
        print(history.head(5))


if __name__ == "__main__":
    main()
