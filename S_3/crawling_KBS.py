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
- KBS 메인은 JS로 렌더되는 경우가 많아, 초기 HTML로는 기사를 못 찾음 .
  Network 탭에서 확인한 JSON 엔드포인트(API_URL)를 사용한다.
- JSON 구조는 상황에 따라 '최상위 리스트' 또는 {'items':[...]} 두 형태를 모두 대응.
"""

# 공통 유틸
def to_abs_url(href: str) -> str:
    """상대 경로를 절대 경로로 변환한다."""
    if not href:
        return ''  # None/빈 문자열 방지: 호출부에서 안전하게 처리할 수 있도록 빈 값 반환
    if href.startswith('http'):
        return href  # 이미 절대 URL(https://, http://)이면 그대로 반환
    if href.startswith('/'):
        # 루트 상대 경로("/news/view.do?...")면 사이트 베이스(KBS_BASE) 앞에 붙여 절대 URL로
        return f'{KBS_BASE}{href}'
    # 그 외 상대 경로("news/view.do?...")면 앞의 슬래시를 제거해 베이스 뒤에 붙임
    return f'{KBS_BASE}/{href.lstrip("/")}'


def clean_spaces(text: str) -> str:
    """여러 공백/개행을 하나로 줄이고 트림한다."""
    # (text or ''): None 대비. 정규식에서 None이 오면 에러라 빈 문자열로 대체
    # \s+ : 공백/탭/개행 등 연속 공백을 한 칸으로 압축
    # strip(): 앞뒤 여백 제거
    return re.sub(r'\s+', ' ', text or '').strip()


def fetch_html(url: str, *, timeout: int = 10) -> str:
    """URL에서 HTML 텍스트를 반환한다."""
    # 요청 시 HEADERS를 함께 전송(UA/Referer 등) → 일부 사이트의 차단 회피/정상 응답 유도
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()  # HTTP 4xx/5xx면 예외 발생 → 호출부에서 try/except로 처리

    # 서버가 인코딩을 안 주거나 ISO-8859-1로 잘못 보내는 경우가 있어 보정
    if not resp.encoding or resp.encoding.lower() == 'iso-8859-1':
        # requests의 추정 인코딩(chardet/charset-normalizer 기반)으로 재설정
        resp.encoding = resp.apparent_encoding

    return resp.text  # 디코딩된(unicode) HTML 문자열 반환

# KBS 헤드라인(JSON API)
def fetch_kbs_headlines(max_items: int = 10) -> List[Dict[str, str]]:
    """
    KBS JSON API에서 헤드라인 기사 목록을 가져와
    [{'title': str, 'url': str(절대경로)} ...] 형태로 반환한다.
    """
    # API_URL로 HTTP 요청 (10초 타임아웃, 헤더 포함)
    resp = requests.get(API_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()  # 오류 응답(4xx, 5xx)이면 예외 발생

    # 응답을 JSON으로 변환
    data: Union[List[dict], Dict[str, object]] = resp.json()

    # JSON 최상위 구조가 리스트이거나 딕셔너리일 수 있음 → 둘 다 대응
    if isinstance(data, list):
        # 예: [ {title:..., url:...}, {...} ]
        items = data
    elif isinstance(data, dict):
        # 예: { "items": [ {...}, {...} ] }
        items = data.get('items', [])
        if not isinstance(items, list):
            items = []  # 예상치 못한 구조일 경우 안전하게 빈 리스트 처리
    else:
        items = []

    results: List[Dict[str, str]] = []  # 최종 결과 담을 리스트
    for it in items:
        if not isinstance(it, dict):  # 혹시 리스트 안에 dict 아닌 게 있으면 스킵
            continue
        # 제목(title)과 URL(url) 꺼내기 → 문자열로 변환 후 공백 정리
        title = clean_spaces(str(it.get('title', '')))
        url = to_abs_url(str(it.get('url', '')))  # 상대경로면 절대 URL로 변환
        if not title:  # 제목이 없으면 건너뜀
            continue
        results.append({'title': title, 'url': url})  # 결과에 추가
        if len(results) >= max_items:  # 최대 개수 제한
            break
    return results

def print_kbs_headlines(items: List[Dict[str, str]]) -> None:
    """
    KBS 헤드라인을 번호와 함께 출력한다(제목 + URL).
    뉴스 리스트를 받아 제목과 URL을 보기 좋게 번호 매겨 출력하는 함수
    """
    print('[KBS 헤드라인]')
    if not items:
        # 수집 결과가 비어있으면 안내 메시지 출력
        print('- 수집된 항목이 없습니다.')
        return
    # enumerate(items, 1) → 인덱스 1부터 번호 매기기
    for idx, it in enumerate(items, 1):
        title = it.get('title', '')  # 딕셔너리에서 제목 꺼내기
        url = it.get('url', '')      # 딕셔너리에서 URL 꺼내기
        print(f'{idx}. {title}')     # 번호 + 제목 출력
        if url:                      # URL이 존재하면 밑줄로 출력
            print(f'   - {url}')



# 보너스: 네이버 금융 지수
def parse_naver_kospi_kosdaq(html: str) -> Tuple[Optional[str], Optional[str]]:
    """
    네이버 금융(시세) 페이지에서 KOSPI, KOSDAQ 지수를 파싱한다.
    - 대표 ID(#KOSPI_now, #KOSDAQ_now) 우선
    - 실패 시 간단 폴백(텍스트 근처 숫자 추출)
    """
    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(html, 'html.parser')

    kospi = None   # 최종적으로 반환할 KOSPI 값
    kosdaq = None  # 최종적으로 반환할 KOSDAQ 값

    # 1) 먼저 공식적으로 존재하는 ID를 통해 바로 추출
    node = soup.select_one('#KOSPI_now')   # <span id="KOSPI_now">2,500.35</span>
    if node:
        kospi = clean_spaces(node.get_text())  # 공백 정리 후 문자열 저장

    node = soup.select_one('#KOSDAQ_now')  # <span id="KOSDAQ_now">820.55</span>
    if node:
        kosdaq = clean_spaces(node.get_text())

    # 2) 만약 위에서 못 찾으면(페이지 구조가 변경된 경우)
    #    "KOSPI"라는 글자를 가진 텍스트를 찾아서 그 주변에서 숫자만 추출
    if kospi is None:
        txt = soup.find(string=re.compile(r'KOSPI', re.I))  # "KOSPI"라는 단어 검색
        if txt:
            near = getattr(txt, 'parent', None)  # 텍스트의 부모 태그 가져오기
            near_text = clean_spaces(near.get_text()) if near else str(txt)
            # 숫자 패턴(정수 또는 소수)만 정규식으로 뽑음
            m = re.search(r'([0-9]+(?:\.[0-9]+)?)', near_text)
            if m:
                kospi = m.group(1)

    # 3) KOSDAQ도 동일한 방식으로 폴백
    if kosdaq is None:
        txt = soup.find(string=re.compile(r'KOSDAQ', re.I))
        if txt:
            near = getattr(txt, 'parent', None)
            near_text = clean_spaces(near.get_text()) if near else str(txt)
            m = re.search(r'([0-9]+(?:\.[0-9]+)?)', near_text)
            if m:
                kosdaq = m.group(1)

    # 4) (KOSPI, KOSDAQ) 값을 튜플로 반환
    return kospi, kosdaq



def parse_naver_usdkrw(html: str) -> Optional[str]: # 매개변수: html (네이버 환율 페이지의 HTML 문자열)
    """
    네이버 금융(시장지표)에서 USD/KRW 환율 값을 파싱한다.
    - '미국 USD' 행의 .value 값 우선
    """
    soup = BeautifulSoup(html, 'html.parser') #HTML 문자열을 BeautifulSoup 객체로 변환 → CSS 선택자로 탐색 가능해짐.
    for row in soup.select('#exchangeList li'): #CSS 선택자 #exchangeList li → <ul id="exchangeList"> 안의 <li> 항목들 반복.
        if '미국 USD' in row.get_text(' ', strip=True): # 각 <li> 항목에서 '미국 USD'라는 텍스트가 포함된 항목을 찾음
            val = row.select_one('.value') # 해당 <li> 안에서 class="value"인 태그를 찾음 (환율 값이 들어있음)
            if val:
                return clean_spaces(val.get_text()) # 환율 값을 텍스트로 추출해서 반환 (공백 정리)
    return None # 만약 '미국 USD' 항목을 못 찾으면 None 반환


def print_bonus_market() -> None:
    """보너스: KOSPI/KOSDAQ/달러환율 간단 출력."""
    try:
        sise_html = fetch_html(NAVER_SISE) # 네이버 금융 시세 페이지(주식) HTML 요청.
        kospi, kosdaq = parse_naver_kospi_kosdaq(sise_html) # HTML을 파싱해서 KOSPI, KOSDAQ 값 추출.
    except Exception as exc:
        kospi, kosdaq = None, None
        print(f'[보너스] 네이버 시세 요청 실패: {exc}') # kospi, kosdaq = None 으로 설정하고 에러 메시지 출력.

    try:
        fx_html = fetch_html(NAVER_FX) #네이버 환율 페이지 HTML 요청.
        usdkrw = parse_naver_usdkrw(fx_html) #HTML을 파싱해서 달러/원 환율 값 추출.
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
