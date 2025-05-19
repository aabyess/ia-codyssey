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

# 문자 집합 및 암호 길이 설정
CHARSET = string.ascii_lowercase + string.digits
PASSWORD_LENGTH = 6

# 시스템 CPU 코어 수 확인
PROCESS_COUNT = multiprocessing.cpu_count()

# 시작 시간과 전체 시도 횟수를 저장할 공유 변수
start_time = time.time()
attempt_counter = multiprocessing.Value('i', 0)

def try_passwords(start_chars, prefix, counter):
    """
    주어진 시작 문자들로 가능한 암호를 조합해 압축 해제를 시도함.
    """
    try:
        with zipfile.ZipFile(ZIP_FILE) as zf:
            for start_char in start_chars:
                for pwd_tuple in itertools.product(CHARSET, repeat=PASSWORD_LENGTH - len(prefix) - 1):
                    password = prefix + start_char + ''.join(pwd_tuple)

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
                            f.flush()
                            time.sleep(0.1)  # 디스크 기록 시간 확보

                        os._exit(0)
                    except:
                        if count % 1000 == 0:
                            print(f"[{prefix+start_char}] {count}회 시도 중... 경과 시간: {time.time() - start_time:.2f}초")

    except Exception as e:
        print(f"[!] 오류 발생: {e}")

def run_crack(prefix):
    """
    prefix를 기반으로 프로세스를 분할 실행
    """
    print(f"[*] 시작 단계: prefix='{prefix}'")
    start_chars = CHARSET[:PROCESS_COUNT]  # 코어 수만큼 시작 문자 분배
    processes = []

    for i in range(PROCESS_COUNT):
        chs = CHARSET[i::PROCESS_COUNT]  # 문자 집합을 분산 처리
        p = multiprocessing.Process(target=try_passwords, args=(chs, prefix, attempt_counter))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

def unlock_zip():
    """
    'mars'로 시작하는 암호 먼저 시도하고, 실패 시 전체 6자리 암호 시도
    """
    global start_time
    print(f"[*] 멀티코어 암호 해독 시작 (CPU 코어 수: {PROCESS_COUNT})")

    # 1단계: marsxx 형식 우선 시도
    start_time = time.time()
    run_crack("mars")

    # password.txt가 생성되지 않았으면 전체 탐색 시도
    if not os.path.exists(OUTPUT_FILE):
        print("[*] marsxx 실패, 전체 탐색 시도 중...")
        attempt_counter.value = 0  # 카운터 초기화
        start_time = time.time()
        run_crack("")

if __name__ == "__main__":
    unlock_zip()
