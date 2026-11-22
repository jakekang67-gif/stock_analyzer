# 주식 데이터 분석기

yfinance로 주가를 조회하고, Plotly 차트로 분석하는 Streamlit 앱입니다.

## 기능

- **단일 종목 분석**
  - 선 차트 / 캔들스틱 차트 (상승 파란 · 하락 빨강)
  - 캔들스틱 하단 거래량 막대 (고거래량 강조, X축 연동)
  - MA20(주황) · MA60(초록) 표시/숨김
- **종목 비교**: 여러 종목을 시작일=100으로 정규화해 수익률 비교
- **사이드바 수익률 계산기**: 매수일·금액 기준 현재 가치·수익률 계산

## 로컬 실행

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속합니다.

## 사용법

1. 기간을 선택한 뒤 **단일 종목** 또는 **종목 비교** 탭을 사용합니다.
2. 단일 종목: 코드 입력 후 **데이터 조회** (예: `005930.KS`, `AAPL`)
3. 종목 비교: 쉼표로 여러 코드 입력 후 **비교 조회** (예: `005930.KS, 000660.KS`)
4. 왼쪽 사이드바에서 매수 날짜·금액으로 수익률을 계산할 수 있습니다.

## 프로젝트 구조

| 파일 | 설명 |
|------|------|
| `app.py` | 메인 Streamlit 앱 |
| `stocks.py` | 종목 이름/코드 카탈로그 |
| `app_full.py` | 확장 기능 백업(검색·음성 등) |
| `test_samsung_stock.py` / `test_apple_stock.py` | yfinance 조회 테스트 |

## 주의

투자 권유가 아니며, 참고용 분석 도구입니다. 데이터는 Yahoo Finance(yfinance)에 의존합니다.
