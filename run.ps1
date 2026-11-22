# 주식 데이터 분석기 실행 (가상환경 + Streamlit)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Error "venv 가 없습니다. 먼저: python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}

& ".\venv\Scripts\Activate.ps1"
# SSL 우회는 app.py 의 ssl_fix 이 처리합니다.
streamlit run app.py
