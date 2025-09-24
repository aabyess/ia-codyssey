# crawling_KBS.py
# -*- coding: utf-8 -*-
"""
KBS 헤드라인 뉴스 크롤러 (+ 보너스: 네이버 금융 지수)
- 표준 라이브러리 + requests + BeautifulSoup만 사용
- PEP 8 코딩 스타일 준수
- 문자열은 기본적으로 작은따옴표(' ') 사용

기능 개요
1) KBS 메인 페이지에서 '헤드라인' 뉴스 타이틀 수집
   - 섹션 제목에 '헤드라인'이 포함된 영역 우선 탐색
   - 실패 시 문서 전체를 훑으며 폭넓은 링크 패턴으로 폴백
   - 메뉴/배너류 텍스트 필터링
2) 수집 결과를 리스트(List[str])로 화면 출력
3) 보너스: 네이버 금융에서 KOSPI, KOSDAQ, USD/KRW 간단 수집
"""

from __future__ import annotations

import re
import sys
from typing import Iterable, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

KBS_BASE = 'https://news.kbs.co.kr'
KBS_MAIN = 'https://news.kbs.co.kr/'
NAVER_SISE = 'https://finance.naver.com/sise/'
NAVER_FX = 'https://finance.naver.com/marketindex/'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

# 기사로 보기 어려운 잡텍스트 블록리스트
BLOCK_WORDS = {'전체보기', '더보기', '영상으로 보기', '바로가기', 'LIVE', 'KBS 뉴스', '뉴스홈'}


# -----------------------
# 공통 유틸
# -----------------------
def fetch_html(url: str, *, timeout: int = 10) -> str:
    """URL의 HTML을 요청해 문자열로 반환한다."""
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    if not resp.encoding or resp.encoding.lower() == 'iso-8859-1':
        resp.encoding = resp.apparent_encoding
    return resp.text


def to_abs_url(href: str) -> str:
    """상대경로를 절대경로로 변환한다."""
    if href.startswith('http'):
        return href
    if href.startswith('/'):
        return f'{KBS_BASE}{href}'
    return f'{KBS_MAIN.rstrip("/")}/{href}'


def clean_title(text: str) -> str:
    """제목 문자열에서 공백/개행을 정리한다."""
    return re.sub(r'\s+', ' ', text).strip()


def is_bad_title(title: str) -> bool:
    """메뉴/내비게이션 등 기사로 보기 어려운 제목을 걸러낸다."""
    if not title:
        return True
    if title in BLOCK_WORDS:
        return True
    if len(title) < 6:
        return True
    return False


# -----------------------
# KBS 헤드라인 파싱
# -----------------------
def is_news_link(a: Tag) -> bool:
    """KBS 뉴스 본문 링크로 '추정'되는 패턴을 폭넓게 허용한다."""
    href = a.get('href', '')
    if not href:
        return False

    # 대표 패턴을 넓게 커버:
    # - /news/view.do?..., /news/.../view/..., /news/.../read/..., /news/.../v/...
    # - /news/.../<숫자> (아이디형)
    # - 절대 URL일 경우 news.kbs.co.kr만 허용
    pattern = re.compile(
        r'^(?:https?://news\.kbs\.co\.kr)?/?news/(?:.+?(?:view|read|v)\b|.+?/\d{6,})',
        re.IGNORECASE
    )
    return bool(pattern.search(href))


def find_headline_section(soup: BeautifulSoup) -> Optional[Tag]:
    """
    문서에서 '헤드라인' 섹션 컨테이너를 찾아 반환한다.
    - h2/h3/aria-label 등에 '헤드라인' 텍스트가 포함된 영역 우선
    """
    for heading in soup.find_all(['h2', 'h3']):
        if heading.get_text(strip=True).find('헤드라인') != -1:
            return heading.parent

    for sec in soup.find_all(attrs={'aria-label': True}):
        label = str(sec.get('aria-label', ''))
        if '헤드라인' in label:
            return sec

    return None


def extract_links_from_container(container: Tag, limit: int = 20) -> List[Tuple[str, str]]:
    """
    컨테이너(또는 문서 전체)에서 기사 링크를 추출한다.
    - 폭넓은 링크 패턴을 사용
    - 블록리스트/짧은 텍스트 제거
    """
    pairs: List[Tuple[str, str]] = []
    seen: set = set()

    for a in container.find_all('a', href=True):
        if not is_news_link(a):
            continue
        title = clean_title(a.get_text(' ', strip=True))
        if is_bad_title(title):
            continue
        href = to_abs_url(a['href'])
        key = (title, href)
        if key in seen:
            continue
        pairs.append((title, href))
        seen.add(key)
        if len(pairs) >= limit:
            break

    return pairs


def parse_kbs_headlines(html: str, *, max_items: int = 10) -> List[str]:
    """
    KBS 메인 HTML에서 헤드라인 뉴스 타이틀 목록을 추출해 List[str]로 반환한다.
    - 섹션 매칭 실패 시 문서 전체에서 폴백
    """
    soup = BeautifulSoup(html, 'html.parser')

    container = find_headline_section(soup)
    items: List[Tuple[str, str]] = []

    if container is not None:
        items = extract_links_from_container(container, limit=max_items * 3)

    if not items:
        items = extract_links_from_container(soup, limit=max_items * 6)

    titles_only = [t for t, _ in items][:max_items]
    return titles_only


def print_as_list(items: Iterable[str]) -> None:
    """리스트 객체를 번호와 함께 화면에 출력한다."""
    items = list(items)
    print('[KBS 헤드라인]')
    if not items:
        print('- 수집된 항목이 없습니다.')
        return
    for idx, title in enumerate(items, start=1):
        print(f'{idx}. {title}')


# -----------------------
# 보너스: 간단한 금융 지수
# -----------------------
def parse_naver_kospi_kosdaq(html: str) -> Tuple[Optional[str], Optional[str]]:
    """네이버 금융(시세) 페이지에서 KOSPI, KOSDAQ 지수를 파싱한다."""
    soup = BeautifulSoup(html, 'html.parser')

    kospi = None
    kosdaq = None

    node = soup.select_one('#KOSPI_now')
    if node:
        kospi = clean_title(node.get_text())

    node = soup.select_one('#KOSDAQ_now')
    if node:
        kosdaq = clean_title(node.get_text())

    if kospi is None:
        text = soup.find(string=re.compile(r'KOSPI', re.I))
        if text and isinstance(text, str):
            parent_text = getattr(text, 'parent', None)
            parent_text = parent_text.get_text(' ', strip=True) if parent_text else text
            m = re.search(r'([0-9]+(?:\.[0-9]+)?)', parent_text)
            if m:
                kospi = m.group(1)

    if kosdaq is None:
        text = soup.find(string=re.compile(r'KOSDAQ', re.I))
        if text and isinstance(text, str):
            parent_text = getattr(text, 'parent', None)
            parent_text = parent_text.get_text(' ', strip=True) if parent_text else text
            m = re.search(r'([0-9]+(?:\.[0-9]+)?)', parent_text)
            if m:
                kosdaq = m.group(1)

    return kospi, kosdaq


def parse_naver_usdkrw(html: str) -> Optional[str]:
    """네이버 금융(시장지표)에서 USD/KRW 환율 값을 파싱한다."""
    soup = BeautifulSoup(html, 'html.parser')

    usd_row = None
    for row in soup.select('#exchangeList li'):
        if '미국 USD' in row.get_text(' ', strip=True):
            usd_row = row
            break

    if usd_row:
        val = usd_row.select_one('.value')
        if val:
            return clean_title(val.get_text())

    text = soup.find(string=re.compile(r'미국\s*USD'))
    if text:
        nearby = text.parent.get_text(' ', strip=True)
        m = re.search(r'([0-9]+(?:\.[0-9]+)?)', nearby)
        if m:
            return m.group(1)

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


# -----------------------
# 실행부
# -----------------------
def main() -> None:
    """엔트리 포인트: KBS 헤드라인 수집 및 출력 + 보너스 지수 출력."""
    try:
        html = fetch_html(KBS_MAIN)
    except Exception as exc:
        print('[오류] KBS 페이지 요청 실패:', exc)
        sys.exit(1)

    titles = parse_kbs_headlines(html, max_items=10)
    print_as_list(titles)

    # 보너스 출력
    print_bonus_market()


if __name__ == '__main__':
    main()
