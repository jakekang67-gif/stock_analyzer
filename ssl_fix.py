"""
Windows에서 사용자 경로에 한글이 있으면 curl_cffi(yfinance)가
certifi CA 파일을 읽지 못하는 문제를 우회합니다.

yfinance / curl_cffi 를 import 하기 *전에* 반드시 호출해야 합니다.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


# curl이 안정적으로 읽는 ASCII 전용 경로 (Windows)
_WINDOWS_CA_DIR = Path(r"C:\Temp")
_WINDOWS_CA_FILE = _WINDOWS_CA_DIR / "stock_analyzer_cacert.pem"


def ensure_ascii_ca_bundle() -> str | None:
    """
    CA 번들을 ASCII 경로에 두고 SSL 관련 환경 변수를 설정합니다.
    Windows가 아니면 아무 것도 하지 않고 None을 반환합니다.
    """
    if sys.platform != "win32":
        return None

    try:
        import certifi
    except ImportError:
        return None

    src = Path(certifi.where())
    if not src.is_file():
        return None

    try:
        _WINDOWS_CA_DIR.mkdir(parents=True, exist_ok=True)
        # 내용이 바뀌었을 수 있으므로 매번 동기화
        shutil.copy2(src, _WINDOWS_CA_FILE)
        ca_path = str(_WINDOWS_CA_FILE)
    except OSError:
        return None

    for key in ("CURL_CA_BUNDLE", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"):
        os.environ[key] = ca_path

    return ca_path


# 모듈 import 시점에 바로 적용
ensure_ascii_ca_bundle()
