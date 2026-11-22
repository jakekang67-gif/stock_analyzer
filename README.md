# 상승 추세를 찾는 주식 데이터 분석기

야후 파이낸스 데이터와 이동평균(MA)으로 상승 추세를 확인하는 Streamlit 앱입니다.

## 로컬 실행

```bash
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 사용법

1. 사이드바에서 종목 코드 입력 (예: `AAPL`, `005930.KS`)
2. 조회 기간·이동평균 설정
3. **분석하기** 클릭

모바일에서는 왼쪽 위 메뉴(≫)에서 설정을 열 수 있습니다.

## 주의

투자 권유가 아니며, 참고용 분석 도구입니다.
