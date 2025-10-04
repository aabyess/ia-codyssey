import os
import random
import time
import getpass
from typing import List
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


NAVER_LOGIN = 'https://nid.naver.com/nidlogin.login'
NAVER_MAIL_INBOX = 'https://mail.naver.com/v2/folders/0/all'

# 실행 시점에 입력을 받도록 수정
NAVER_ID = input("네이버 아이디를 입력하세요: ").strip()
NAVER_PW = getpass.getpass("네이버 비밀번호를 입력하세요: ").strip()


def human_sleep(a: float, b: float) -> None:
    time.sleep(random.uniform(a, b)) #a와 b 사이의 임의(random) 시간 동안 멈춤.


#주어진 문자열(text)을 입력창(elem)에 한 글자씩 타이핑.
def human_type(elem, text: str, per_key_min: float = 0.05, per_key_max: float = 0.18) -> None:
    for ch in text:
        elem.send_keys(ch)
        human_sleep(per_key_min, per_key_max) #각 글자마다 human_sleep()을 호출해서 랜덤한 지연을 줌.


# 크롬 브라우저를 자동으로 띄울 때 설정을 넣는 함수.
def make_driver() -> webdriver.Chrome:
    opts = ChromeOptions()
    opts.add_argument('--disable-blink-features=AutomationControlled') #크롬이 “자동화된 브라우저(봇)”이라고 웹사이트에 티내는 걸 조금 줄여줌.
    opts.add_argument('--start-maximized') #브라우저를 시작할 때 최대화 상태로 열기.
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30) #페이지가 30초 안에 안 뜨면 에러 발생시키도록 제한.
    return driver

#아이디 입력창이 보일 때까지 10초 기다리라는 함수
def wait_visible(driver, locator: tuple, timeout: int = 15): 
    return WebDriverWait(driver, timeout).until(  #driver 객체를 대상으로 최대 timeout초 기다리겠다.
                                                  #driver: 지금 열려 있는 브라우저 객체
        EC.visibility_of_element_located(locator) #locator 조건을 만족해서 요소가 DOM에 있고, 보이는 상태일 때 반환.
                                                  #셀레니움에서 locator(로케이터) 는 "어떤 요소를 찾아야 하는지"를 지정하는 방법.
                                                  #EC = expected_conditions (셀레니움에서 제공하는 “조건” 세트).
    )



def login_slow(driver) -> bool:
    """네이버 로그인: 사람처럼 입력 후 받은메일함 진입 여부 반환(True/False)."""
    if not NAVER_ID or not NAVER_PW:                                      # (사전조건) 아이디/비번은 환경변수로 받아옴
        raise RuntimeError('환경변수 NAVER_ID / NAVER_PW를 설정하세요.')

    driver.get(NAVER_LOGIN)                                               # 네이버 로그인 페이지로 이동

    # 1) 아이디/비밀번호 입력창 대기 후 입력 (여러 후보 중 먼저 보이는 것 사용)
    id_input = None
    for loc in [(By.ID, 'id'), (By.NAME, 'id')]:                          # id 필드를 찾는 방법 후보(변경 대비)
        try:
            id_input = wait_visible(driver, loc, timeout=10)              # 요소가 "보일 때"까지 최대 10초 기다림
            break                                                         # 첫 번째로 잡히는 요소 사용
        except Exception:
            pass
    if id_input is None:                                                  # 입력창을 못 찾았으면 실패로 종료
        raise RuntimeError('아이디 입력창을 찾지 못했습니다.')

    id_input.clear()                                                      # 기존 값 제거
    human_sleep(0.2, 0.5)                                                 # 자연스러운 지연(사람 흉내)
    human_type(id_input, NAVER_ID, 0.08, 0.18)                            # 아이디를 "한 글자씩" 랜덤 딜레이로 타이핑
    #    └ per_key_min=0.08s, per_key_max=0.18s → 너무 빠르면 봇 의심, 느리면 안전(필요시 ↑)

    pw_input = None
    for loc in [(By.ID, 'pw'), (By.NAME, 'pw')]:                          # pw 필드도 다중 후보로 탐색
        try:
            pw_input = wait_visible(driver, loc, timeout=10)
            break
        except Exception:
            pass
    if pw_input is None:
        raise RuntimeError('비밀번호 입력창을 찾지 못했습니다.')

    pw_input.clear()
    human_sleep(0.2, 0.5)
    human_type(pw_input, NAVER_PW, 0.09, 0.22)                            # 비밀번호 타이핑(조금 더 느리게)
    #    └ 비번은 보안 민감 → 속도 더 느리게(탐지 회피 목적)

    # 2) 로그인 제출(버튼 없으면 엔터로 대체)
    clicked = False
    for loc in [
        (By.ID, 'log.login'),                                             # 네이버 구형 버튼 id
        (By.CSS_SELECTOR, 'button[type="submit"]'),                       # 표준 제출 버튼
        (By.CSS_SELECTOR, 'button.btn_login'),                            # 클래스명 기반 후보
    ]:
        try:
            driver.find_element(*loc).click()                              # 위 후보 중 클릭 가능한 것을 즉시 클릭
            clicked = True
            break
        except Exception:
            pass
    if not clicked:
        pw_input.send_keys(Keys.ENTER)                                    # 버튼 못 찾으면 Enter 키로 제출(대안)

    # 3) 캡챠가 뜨면 수동 해결 시간만 잠깐 부여(간단 버전)
    human_sleep(1.0, 1.6)                                                 # 서버 응답/리다이렉트 잠깐 대기
    page = driver.page_source
    if any(k in page for k in ['자동입력', '보안문자', '자동 입력 방지']):  # 페이지 텍스트로 캡챠/추가인증 감지(휴리스틱)
        print('[INFO] 캡챠/추가 인증 감지. 60초 대기하니 브라우저에서 해결해줘.')
        for _ in range(12):                                                # 총 60초 대기(5초 × 12회)
            time.sleep(5)                                                  # → 사용자가 브라우저에서 직접 캡챠 입력

    # 4) 받은메일함 진입 시도 후 성공 판정(제목 요소 존재 여부)
    driver.get(NAVER_MAIL_INBOX)                                          # 로그인 성공 시 접근 가능한 메일함 URL로 직행
    human_sleep(0.6, 1.2)
    try:
        WebDriverWait(driver, 8).until(                                    # 메일 목록의 "제목" 요소가 DOM에 생길 때까지 대기
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-subject]')),
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[title]')),
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[title]')),
            )
        )
        return True                                                        # 제목 요소 보이면 로그인 성공으로 판단
    except Exception:
        return False                                                       # 제한 시간 내 요소 못 찾으면 실패로 판단



def collect_mail_subjects(driver, limit: int = 30) -> List[str]:
    """메일 목록에서 제목 텍스트를 최대 limit개 수집."""
    subjects: List[str] = []                                               # 결과를 담을 리스트 초기화

    # 다양한 셀렉터 시도 (네이버 메일 DOM 구조가 수시로 바뀌므로 여러 후보 준비)
    selectors = [
        '[data-subject]',                                                  # HTML 속성 data-subject 가진 요소
        'a[title]',                                                        # <a title="..."> 형태의 요소
        'span[title]',                                                     # <span title="..."> 형태의 요소
        'a.mail_title',                                                    # class="mail_title" 가진 <a> 태그
    ]
    for sel in selectors:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)             # 주어진 CSS 셀렉터로 모든 요소 찾기
            for e in elems:
                txt = (e.get_attribute('data-subject') or                  # 1순위: data-subject 속성 값
                       e.get_attribute('title') or                         # 2순위: title 속성 값
                       e.text or '').strip()                               # 3순위: 태그 안의 텍스트
                if txt and txt not in subjects:                            # 값이 있고, 아직 리스트에 없으면 추가
                    subjects.append(txt)
                if len(subjects) >= limit:                                 # 지정한 개수(limit)에 도달하면 즉시 반환
                    return subjects
        except Exception:                                                  # 셀렉터가 없는 경우(구조 변경 등) → 무시하고 다음 셀렉터로 진행
            continue
    return subjects                                                         # 모든 셀렉터 확인 후 수집된 제목 리스트 반환

def main() -> None:
    print('──────────────── 로그인 시도 ────────────────')
    driver = make_driver()
    ok = False
    try:
        ok = login_slow(driver)
        if not ok:
            print('[WARN] 로그인 실패로 판단(여전히 게이트). 쿠키/캡챠 상태를 확인하세요.')
            return

        print('[OK] 로그인 성공으로 판단. 받은메일함 진입 시도.')
        driver.get(NAVER_MAIL_INBOX)
        human_sleep(0.5, 1.0)

        titles = collect_mail_subjects(driver, limit=30)
        if not titles:
            print('[INFO] 제목을 찾지 못했습니다. DOM 구조 변경 가능성 (셀렉터를 조정하세요).')
            return

        print('\n[받은 메일 제목 Top N]')
        for i, t in enumerate(titles, 1):
            print(f'{i}. {t}')
    finally:
        # 필요시 닫지 않고 눈으로 확인하려면 주석 처리
        driver.quit()


if __name__ == '__main__':
    main()
