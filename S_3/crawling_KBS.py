from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union
import re
import sys

import requests
from bs4 import BeautifulSoup

# 설정값: 필요한 경우 여기만 바꾸면 됨
KBS_BASE = 'https://news.kbs.co.kr'
# 네가 Network 탭에서 확인한 JSON 주소를 넣으면 됨(예시 값)
API_URL = 'https://news.kbs.co.kr/expose/329.json?d=202509251726'

# 보너스(네이버 금융)
NAVER_SISE = 'https://finance.naver.com/sise/'
NAVER_FX = 'https://finance.naver.com/marketindex/'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Referer': 'https://news.kbs.co.kr/',
}

"""
KBS 헤드라인 크롤러 (+ 보너스: 네이버 금융 지수)

구성
1) KBS 메인 JSON API(예: /expose/329.json)를 직접 호출해 헤드라인 제목/URL 수집
2) 수집 결과를 번호와 함께 출력(제목 + 절대 URL)
3) 보너스: 네이버 금융에서 KOSPI, KOSDAQ, USD/KRW 환율 간단 수집 및 출력

주의
- KBS 메인은 JS로 렌더되는 경우가 많아, 초기 HTML로는 기사를 못 얻을 수 있음.
  Network 탭에서 확인한 JSON 엔드포인트(API_URL)를 사용한다.
- JSON 구조는 상황에 따라 '최상위 리스트' 또는 {'items':[...]} 두 형태를 모두 대응.
"""

# 공통 유틸
def to_abs_url(href: str) -> str:
    """상대 경로를 절대 경로로 변환한다."""
    if not href:
        return ''
    if href.startswith('http'):
        return href
    if href.startswith('/'):
        return f'{KBS_BASE}{href}'
    return f'{KBS_BASE}/{href.lstrip("/")}'


def clean_spaces(text: str) -> str:
    """여러 공백/개행을 하나로 줄이고 트림한다."""
    return re.sub(r'\s+', ' ', text or '').strip()


def fetch_html(url: str, *, timeout: int = 10) -> str:
    """URL에서 HTML 텍스트를 반환한다."""
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    if not resp.encoding or resp.encoding.lower() == 'iso-8859-1':
        resp.encoding = resp.apparent_encoding
    return resp.text

# 1) KBS 헤드라인(JSON API)
def fetch_kbs_headlines(max_items: int = 10) -> List[Dict[str, str]]:
    """
    KBS JSON API에서 헤드라인 기사 목록을 가져와
    [{'title': str, 'url': str(절대경로)} ...] 형태로 반환한다.
    """
    resp = requests.get(API_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    data: Union[List[dict], Dict[str, object]] = resp.json()

    # JSON 최상위가 리스트인 경우와 dict인 경우 모두 대응
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get('items', [])  # {'items':[...]} 형태
        if not isinstance(items, list):
            items = []
    else:
        items = []

    results: List[Dict[str, str]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        title = clean_spaces(str(it.get('title', '')))
        url = to_abs_url(str(it.get('url', '')))
        if not title:
            continue
        results.append({'title': title, 'url': url})
        if len(results) >= max_items:
            break
    return results


def print_kbs_headlines(items: List[Dict[str, str]]) -> None:
    """KBS 헤드라인을 번호와 함께 출력한다(제목 + URL)."""
    print('[KBS 헤드라인]')
    if not items:
        print('- 수집된 항목이 없습니다.')
        return
    for idx, it in enumerate(items, 1):
        title = it.get('title', '')
        url = it.get('url', '')
        print(f'{idx}. {title}')
        if url:
            print(f'   - {url}')


# -----------------------------
# 2) 보너스: 네이버 금융 지수
# -----------------------------
def parse_naver_kospi_kosdaq(html: str) -> Tuple[Optional[str], Optional[str]]:
    """
    네이버 금융(시세) 페이지에서 KOSPI, KOSDAQ 지수를 파싱한다.
    - 대표 ID(#KOSPI_now, #KOSDAQ_now) 우선
    - 실패 시 간단 폴백
    """
    soup = BeautifulSoup(html, 'html.parser')

    kospi = None
    kosdaq = None

    node = soup.select_one('#KOSPI_now')
    if node:
        kospi = clean_spaces(node.get_text())

    node = soup.select_one('#KOSDAQ_now')
    if node:
        kosdaq = clean_spaces(node.get_text())

    # 간단 폴백(신뢰도 낮음): 텍스트 근처에서 숫자 뽑기
    if kospi is None:
        txt = soup.find(string=re.compile(r'KOSPI', re.I))
        if txt:
            near = getattr(txt, 'parent', None)
            near_text = clean_spaces(near.get_text()) if near else str(txt)
            m = re.search(r'([0-9]+(?:\.[0-9]+)?)', near_text)
            if m:
                kospi = m.group(1)

    if kosdaq is None:
        txt = soup.find(string=re.compile(r'KOSDAQ', re.I))
        if txt:
            near = getattr(txt, 'parent', None)
            near_text = clean_spaces(near.get_text()) if near else str(txt)
            m = re.search(r'([0-9]+(?:\.[0-9]+)?)', near_text)
            if m:
                kosdaq = m.group(1)

    return kospi, kosdaq


def parse_naver_usdkrw(html: str) -> Optional[str]:
    """
    네이버 금융(시장지표)에서 USD/KRW 환율 값을 파싱한다.
    - '미국 USD' 행의 .value 값 우선
    """
    soup = BeautifulSoup(html, 'html.parser')
    for row in soup.select('#exchangeList li'):
        if '미국 USD' in row.get_text(' ', strip=True):
            val = row.select_one('.value')
            if val:
                return clean_spaces(val.get_text())
    return None


def print_bonus_market() -> None:
    """보너스: KOSPI/KOSDAQ/달러환율 간단 출력."""
    try:
        sise_html = fetch_html(NAVER_SISE)
        kospi, kosdaq = parse_naver_kospi_kosdaq(sise_html)
    except Exception as exc:
        kospi, kosdaq = None, None
        print(f'[보너스] 네이버 시세 요청 실패: {exc}')

    try:
        fx_html = fetch_html(NAVER_FX)
        usdkrw = parse_naver_usdkrw(fx_html)
    except Exception as exc:
        usdkrw = None
        print(f'[보너스] 네이버 환율 요청 실패: {exc}')

    print('\n[보너스] 네이버 금융 지수')
    print(f'- KOSPI   : {kospi if kospi is not None else "N/A"}')
    print(f'- KOSDAQ  : {kosdaq if kosdaq is not None else "N/A"}')
    print(f'- USD/KRW : {usdkrw if usdkrw is not None else "N/A"}')


def main() -> None:
    # 1) KBS 헤드라인 출력
    try:
        headlines = fetch_kbs_headlines(max_items=10)
    except Exception as exc:
        print('[KBS 헤드라인]')
        print(f'- 수집 실패: {exc}')
    else:
        print_kbs_headlines(headlines)

    # 2) 보너스(네이버 금융) 출력
    print_bonus_market()


if __name__ == '__main__':
    main()
