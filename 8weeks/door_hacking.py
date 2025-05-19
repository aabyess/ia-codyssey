import zipfile  # ZIP 파일을 다루기 위한 라이브러리
import itertools  # 가능한 조합을 만드는 라이브러리
import string  # 문자와 숫자 집합을 사용하기 위한 라이브러리
import multiprocessing  # 여러 CPU 코어를 동시에 활용하기 위한 라이브러리
import time  # 시간 측정용
from datetime import datetime  # 날짜 및 시간을 보기 좋게 표현하기 위함
import os  # 시스템 명령을 사용하기 위한 라이브러리

# 압축 파일과 암호가 발견되면 결과를 저장할 파일 이름 지정
ZIP_FILE = "emergency_storage_key.zip"
OUTPUT_FILE = "password.txt"

# 암호 조건 설정 (소문자 알파벳과 숫자, 총 6자리)
CHARSET = string.ascii_lowercase + string.digits
PASSWORD_LENGTH = 6

# 내 컴퓨터의 CPU 코어 수를 확인해서 사용
PROCESS_COUNT = multiprocessing.cpu_count()

# 시작 시간과 암호 시도 횟수를 기록하는 변수 설정
start_time = time.time()
attempt_counter = multiprocessing.Value('i', 0)

# 특정 문자로 시작하는 암호를 만들어서 ZIP 파일 압축 해제를 시도하는 알고리즘
def try_passwords(start_char, counter):
    try:
        # 압축 파일 열기
        with zipfile.ZipFile(ZIP_FILE) as zf:
            # start_char는 이미 앞에 있으니까, 나머지 5자리를 a~z + 0~9로 조합해서 만들어줌.
            for pwd_tuple in itertools.product(CHARSET, repeat=PASSWORD_LENGTH - 1):
                password = start_char + ''.join(pwd_tuple)

                # 전체 시도 횟수를 기록함. 여러 프로세스가 동시에 작업하니까 충돌 없이 처리하도록 get_lock()을 씀.
                with counter.get_lock():
                    counter.value += 1
                    count = counter.value

                try:
                    # 만든 암호를 가지고 실제 압축을 풀어보는 시도
                    zf.extractall(pwd=password.encode())
                    duration = time.time() - start_time

                    # 성공하면 정보 출력
                    print(f"\n[+] 암호 해제 성공!")
                    print(f"[+] 암호: {password}")
                    print(f"[+] 시작 시간: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"[+] 시도 횟수: {count}")
                    print(f"[+] 소요 시간: {duration:.2f}초")

                    # 암호를 파일에 저장
                    with open(OUTPUT_FILE, "w") as f:
                        f.write(password)

                    # 모든 프로세스를 즉시 종료 (다른 프로세스의 추가 작업 방지)
                    os._exit(0)

                except:
                    # 10,000번마다 진행 상황을 로그로 찍어줌.
                    if count % 10000 == 0:
                        print(f"[{start_char}] {count}회 시도 중... 경과 시간: {time.time() - start_time:.2f}초")

    except Exception as e:
        # 오류가 생겼을 때 안내
        print(f"[!] 오류 발생 in {start_char}: {e}")


# 멀티코어로 동시에 암호를 해제하는 메인 함수.
def unlock_zip():
    # 시작 메시지 출력
    print(f"[*] 멀티코어 암호 해독 시작 (CPU 코어 수: {PROCESS_COUNT})")
    print(f"[*] 시작 시간: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")

    # 각 CPU 코어에 시작 문자를 분배해서 병렬로 작업
    #  a부터 시작, b부터 시작 이런식으로 나눠줌
    start_chars = CHARSET[:PROCESS_COUNT]
    processes = []

    # 프로세스를 생성하고 실행
    for ch in start_chars:
        p = multiprocessing.Process(target=try_passwords, args=(ch, attempt_counter))
        p.start()
        processes.append(p)

    # 모든 프로세스의 작업이 끝날 때까지 기다림
    for p in processes:
        p.join()

# 이 스크립트를 직접 실행할 때 메인 함수를 실행
if __name__ == "__main__":
    unlock_zip()
