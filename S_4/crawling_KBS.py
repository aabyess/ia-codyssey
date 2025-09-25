# crawling_KBS.py
# -*- coding: utf-8 -*-
"""
네이버 로그인 전/후 콘텐츠 비교 + (보너스) 네이버 메일 제목 수집

요약
- Selenium으로 naver.com에 접속해 '비로그인 상태' 콘텐츠와
  '로그인 상태' 콘텐츠의 차이를 확인한다.
- 로그인 후에만 보이는 영역(예: 프로필/메일 박스/알림 등)을 한 가지 선정해
  해당 텍스트를 수집한다.
- 보너스: mail.naver.com으로 이동해 받은메일함 제목 일부를 수집한다.

사전 준비
1) Python 패키지
   - pip install selenium
2) Chrome 브라우저, ChromeDriver 설치
   - Chrome 버전에 맞는 드라이버 다운로드 후 PATH 등록 또는 코드에서 경로 지정
3) 로그인 정보 환경변수로 세팅
   - OS에서:
     set NAVER_ID=your_id
     set NAVER_PW=your_password
   - 또는 코드 하단 main()의 입력부를 직접 문자열로 채워도 됨(보안상 비추천)

주의
- 네이버는 자동화 접근을 탐지/차단할 수 있다.
- 2단계 인증/캡차 등 추가 보안 절차가 나오면 자동화가 중단될 수 있다.
- 실습 목적: 소량 조회, 개인 계정, 비상업적 사용으로 제한하자.

코딩 규칙
- PEP8 스타일(공백, 들여쓰기 등) 준수
- 문자열은 기본 '단일 따옴표' 사용
- 함수명: snake_case
- 클래스명: CapWords (여기서는 사용 없음)
"""

from __future__ import annotations

import os
import sys
import time
from typing import List

# Selenium 기본 구성요소 임포트
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


NAVER_HOME = 'https://www.naver.com/'
NAVER_LOGIN = 'https://nid.naver.com/nidlogin.login'
NAVER_MAIL_INBOX = 'https://mail.naver.com/v2/folders/0'  # 받은메일함(신버전 경로)

# 비교용: 비로그인 상태에서 보이는 대표 요소(로그인 버튼)
SEL_LOGIN_BUTTON = (By.CSS_SELECTOR, 'a#gnb_login_button, a.link_login')

# 비교용: 로그인 후 보이는 대표 요소(프로필/마이 영역)
# 네이버는 UI가 자주 바뀌므로 복수 후보를 둔다.
SEL_PROFILE_AREA_CANDIDATES = [
    (By.CSS_SELECTOR, '#NM_USER_INFO, .MyView-module__container'),   # 상단 사용자 영역
    (By.CSS_SELECTOR, 'a#gnb_logout_button, a#gnb_my_page'),         # 로그아웃/마이페이지 링크
    (By.CSS_SELECTOR, 'div#account, .ico_user'),                     # 계정/프로필 아이콘
]

# 메일 리스트(신버전)에서 제목 텍스트 셀렉터 후보
# 네이버 메일은 개편이 잦으므로 복수 셀렉터를 준비한다.
SEL_MAIL_SUBJECT_CANDIDATES = [
    (By.CSS_SELECTOR, 'div.mailList div.mailItem div.subject span.mail_title'),
    (By.CSS_SELECTOR, 'ul.mail_list li div.mail_title'),
    (By.CSS_SELECTOR, 'div.subject span.strong, .mailList .subject .mail_title'),
]


def build_driver(headless: bool = False) -> WebDriver:
    """
    Chrome WebDriver를 생성해 반환한다.
    headless=True이면 브라우저 창을 띄우지 않고 백그라운드로 동작한다.
    """
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    # 자동화 탐지 완화(보장되진 않음)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1400,900')

    # 로컬에 chromedriver가 PATH에 있다면 executable_path 생략 가능
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(20)
    return driver


def wait_for_any(driver: WebDriver, selectors: List[tuple], timeout: int = 12):
    """
    주어진 셀렉터 후보들 중 '하나라도' 등장할 때까지 대기하고, 발견된 WebElement를 반환한다.
    발견 실패 시 TimeoutException을 그대로 발생시킨다.
    """
    end = time.time() + timeout
    last_exc = None
    while time.time() < end:
        for by, sel in selectors:
            try:
                elem = WebDriverWait(driver, 0.8).until(
                    EC.presence_of_element_located((by, sel))
                )
                if elem:
                    return elem
            except Exception as exc:
                last_exc = exc
        time.sleep(0.2)
    # 마지막 예외를 던져 디버깅에 도움을 준다.
    if last_exc:
        raise last_exc
    raise TimeoutError('elements not found within timeout')


def is_logged_in(driver: WebDriver) -> bool:
    """
    현재 naver.com 페이지에서 '로그인 상태'로 추정되는지 간단 검사.
    - 로그인 버튼이 보이지 않거나
    - 프로필/마이 영역 후보가 보이면 로그인으로 간주
    """
    try:
        # 로그인 버튼이 사라졌다면 로그인 상태일 가능성이 높다.
        login_btns = driver.find_elements(*SEL_LOGIN_BUTTON)
        if not login_btns:
            return True
        # 프로필/마이 영역이 보이면 로그인 상태
        for by, sel in SEL_PROFILE_AREA_CANDIDATES:
            if driver.find_elements(by, sel):
                return True
        return False
    except Exception:
        # DOM이 바뀌어도 기본적으로 False로 처리
        return False


def collect_public_snippets(driver: WebDriver, max_count: int = 5) -> List[str]:
    """
    비로그인 상태에서 홈에 노출되는 일부 텍스트(예: 실시간 검색 블록/뉴스 카드 타이틀)를 수집한다.
    네이버 DOM은 자주 바뀌므로 크래시 없이 '보이는 텍스트' 일부만 가져오도록 느슨하게 설계.
    """
    snippets: List[str] = []
    # 홈 주요 섹션 타이틀 후보(뉴스, 쇼핑, 날씨 등)
    candidates = [
        (By.CSS_SELECTOR, 'section h2, section h3'),
        (By.CSS_SELECTOR, '#NM_FAVORITE, #NM_NEWS_STAND'),
        (By.CSS_SELECTOR, 'a.media_end_head_headline, strong.news_tit'),
    ]
    for by, sel in candidates:
        try:
            elems = driver.find_elements(by, sel)
            for e in elems:
                text = (e.text or '').strip()
                if text and text not in snippets:
                    snippets.append(text)
                if len(snippets) >= max_count:
                    return snippets
        except Exception:
            continue
    return snippets


def login_naver(driver: WebDriver, user_id: str, user_pw: str) -> None:
    """
    네이버 로그인 페이지에서 아이디/비밀번호를 입력해 로그인한다.
    - 2단계 인증/캡차가 뜨면 자동화가 중단될 수 있다(수동 인증 필요).
    """
    driver.get(NAVER_LOGIN)

    # 아이디/비밀번호 입력창은 name 속성 또는 CSS 셀렉터로 찾는다.
    # (네이버가 DOM을 자주 바꾸므로 복수 후보를 둔다.)
    id_candidates = [
        (By.ID, 'id'), (By.NAME, 'id'), (By.CSS_SELECTOR, 'input#id'),
        (By.CSS_SELECTOR, 'input[name="id"]'),
    ]
    pw_candidates = [
        (By.ID, 'pw'), (By.NAME, 'pw'), (By.CSS_SELECTOR, 'input#pw'),
        (By.CSS_SELECTOR, 'input[name="pw"]'),
    ]
    btn_candidates = [
        (By.ID, 'log.login'),
        (By.CSS_SELECTOR, 'button.btn_login, input.btn_login'),
        (By.CSS_SELECTOR, 'button[type="submit"]'),
    ]

    # 아이디 입력
    id_input = wait_for_any(driver, id_candidates, timeout=12)
    id_input.clear()
    id_input.send_keys(user_id)

    # 비밀번호 입력
    pw_input = wait_for_any(driver, pw_candidates, timeout=12)
    pw_input.clear()
    pw_input.send_keys(user_pw)

    # 로그인 버튼 클릭
    try:
        btn = wait_for_any(driver, btn_candidates, timeout=8)
        btn.click()
    except Exception:
        # submit 시도가 더 안정적일 때가 있다.
        pw_input.submit()

    # 홈으로 자동 리디렉션 되거나, 추가 인증 화면이 나올 수 있다.
    # 일단 홈으로 이동을 시도해 상태를 확인한다.
    time.sleep(1.2)
    driver.get(NAVER_HOME)
    WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))


def collect_private_snippets(driver: WebDriver, max_count: int = 5) -> List[str]:
    """
    로그인 후에만 보이는 영역에서 간단한 텍스트들을 수집한다.
    예: 상단 사용자 영역의 환영 문구, 메일 박스 유무, 알림 카운트 등.
    """
    snippets: List[str] = []

    # 프로필/마이 영역 텍스트
    for by, sel in SEL_PROFILE_AREA_CANDIDATES:
        try:
            elems = driver.find_elements(by, sel)
            for e in elems:
                t = (e.text or '').strip()
                if t and t not in snippets:
                    snippets.append(t)
                if len(snippets) >= max_count:
                    return snippets
        except Exception:
            continue

    # 로그인 상태에서만 노출되는 GNB 항목들 일부 덤핑
    try:
        gnb_text = (driver.find_element(By.TAG_NAME, 'body').text or '').strip()
        # 과도한 길이 방지: 대표 키워드만 필터링
        for key in ['메일', '카페', '블로그', '구독', '나의 정보', '알림']:
            if key in gnb_text and key not in snippets:
                snippets.append(key)
            if len(snippets) >= max_count:
                break
    except Exception:
        pass

    return snippets[:max_count]


def scrape_mail_subjects(driver: WebDriver, max_count: int = 10) -> List[str]:
    """
    (보너스) 네이버 메일로 이동해 받은메일함 제목 상위 N개를 수집한다.
    - 신버전 UI 기준 CSS 후보를 순회하며 최대 max_count개를 수집한다.
    """
    subjects: List[str] = []
    driver.get(NAVER_MAIL_INBOX)

    # 메일 프레임이 로드될 때까지 대기
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    time.sleep(1.0)

    # 셀렉터 후보들을 순회하며 제목 수집
    for by, sel in SEL_MAIL_SUBJECT_CANDIDATES:
        try:
            elems = driver.find_elements(by, sel)
            for e in elems:
                t = (e.text or '').strip()
                if t:
                    subjects.append(t)
                if len(subjects) >= max_count:
                    return subjects
        except Exception:
            continue

    return subjects[:max_count]


def main() -> None:
    """프로그램 엔트리포인트: 비교 → 로그인 → 비교 → 메일 제목 수집."""

    # 실행할 때 사용자 입력으로 ID/PW 받기
    user_id = input('네이버 아이디를 입력하세요: ').strip()
    user_pw = input('네이버 비밀번호를 입력하세요: ').strip()

    if not user_id or not user_pw:
        print('[오류] 아이디/비밀번호가 입력되지 않았습니다.')
        sys.exit(1)

    driver = build_driver(headless=False)
    try:
        # 1) 비로그인 상태 접근
        driver.get(NAVER_HOME)
        WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        public_before = collect_public_snippets(driver, max_count=5)
        print('[비로그인 상태 예시 텍스트]')
        for i, t in enumerate(public_before, 1):
            print(f'{i}. {t}')

        # 2) 로그인 수행
        print('\n[로그인 진행 중...]')
        login_naver(driver, user_id, user_pw)
        time.sleep(1.0)

        # 3) 로그인 여부 확인 및 로그인 후 텍스트 수집
        logged = is_logged_in(driver)
        print(f'\n[로그인 상태 확인] logged_in={logged}')
        private_after = collect_private_snippets(driver, max_count=5)
        print('[로그인 후 예시 텍스트]')
        for i, t in enumerate(private_after, 1):
            print(f'{i}. {t}')

        # 4) (보너스) 메일 제목 수집
        print('\n[보너스] 네이버 메일 받은메일함 제목')
        subjects = scrape_mail_subjects(driver, max_count=10)
        if not subjects:
            print('- 메일 제목을 찾지 못했습니다(레이아웃/보안 이슈 가능).')
        else:
            for i, s in enumerate(subjects, 1):
                print(f'{i}. {s}')

    finally:
        driver.quit()



if __name__ == '__main__':
    main()
