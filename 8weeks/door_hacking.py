import zipfile
import itertools
import string
import multiprocessing
import time
from datetime import datetime
import os

# 압축 파일과 결과 저장 파일명
ZIP_FILE = "emergency_storage_key.zip"
OUTPUT_FILE = "password.txt"

# 암호는 소문자+숫자로 된 6자리
CHARSET = string.ascii_lowercase + string.digits
PASSWORD_LENGTH = 6

# 시스템 CPU 코어 수 확인
PROCESS_COUNT = multiprocessing.cpu_count()

# 시작 시간과 전체 시도 횟수를 저장할 공유 변수
start_time = time.time()
attempt_counter = multiprocessing.Value('i', 0)

def try_passwords(start_char, counter):
    """
    하나의 프로세스가 주어진 시작 문자로부터 가능한 6자리 암호를 생성하여 압축 해제를 시도한다.
    """
    try:
        with zipfile.ZipFile(ZIP_FILE) as zf:
            for pwd_tuple in itertools.product(CHARSET, repeat=PASSWORD_LENGTH - 1):
                password = start_char + ''.join(pwd_tuple)

                with counter.get_lock():
                    counter.value += 1
                    count = counter.value

                try:
                    zf.extractall(pwd=password.encode())
                    duration = time.time() - start_time

                    print(f"\n[+] 암호 해제 성공!")
                    print(f"[+] 암호: {password}")
                    print(f"[+] 시작 시간: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"[+] 시도 횟수: {count}")
                    print(f"[+] 소요 시간: {duration:.2f}초")

                    with open(OUTPUT_FILE, "w") as f:
                        f.write(password)

                    os._exit(0)  # 모든 프로세스 강제 종료
                except:
                    if count % 10000 == 0:
                        print(f"[{start_char}] {count}회 시도 중... 경과 시간: {time.time() - start_time:.2f}초")

    except Exception as e:
        print(f"[!] 오류 발생 in {start_char}: {e}")

def unlock_zip():
    """
    멀티코어로 암호를 병렬로 해제하는 메인 함수.
    과제 요구사항에 맞춰 이름은 unlock_zip으로 정의.
    """
    print(f"[*] 멀티코어 해킹 시작 (사용 코어 수: {PROCESS_COUNT})")
    print(f"[*] 시작 시간: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")

    # 시작 문자 분배 (CPU 코어 수만큼 분할)
    start_chars = CHARSET[:PROCESS_COUNT]
    processes = []

    for ch in start_chars:
        p = multiprocessing.Process(target=try_passwords, args=(ch, attempt_counter))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

# 프로그램 시작
if __name__ == "__main__":
    unlock_zip()
