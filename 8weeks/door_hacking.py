import zipfile
import itertools
import string
import time
from datetime import datetime

def unlock_zip():
    zip_path = "emergency_storage_key.zip"
    output_file = "password.txt"
    charset = string.ascii_lowercase + string.digits  # a-z + 0-9
    max_length = 6  # 6자리 비밀번호
    count = 0

    try:
        with zipfile.ZipFile(zip_path) as zf:
            print("[*] 암호 대입 시작")
            start_time = time.time()

            # 모든 가능한 6자리 조합 생성
            for pwd_tuple in itertools.product(charset, repeat=max_length):
                password = ''.join(pwd_tuple)
                count += 1

                try:
                    zf.extractall(pwd=password.encode('utf-8'))
                    end_time = time.time()

                    print("\n[+] 성공! 암호:", password)
                    print("[+] 시도 횟수:", count)
                    print("[+] 시작 시간:", datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'))
                    print("[+] 종료 시간:", datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S'))
                    print("[+] 소요 시간: {:.2f}초".format(end_time - start_time))

                    with open(output_file, "w") as f:
                        f.write(password)
                    return
                except:
                    if count % 10000 == 0:
                        print(f"[-] {count}회 시도 중... 경과 시간: {time.time() - start_time:.2f}초")

            print("[-] 암호를 찾지 못했습니다.")
    except FileNotFoundError:
        print("ZIP 파일을 찾을 수 없습니다.")
    except zipfile.BadZipFile:
        print("ZIP 파일이 손상되었습니다.")
    except Exception as e:
        print("오류 발생:", e)

# 메인 함수 실행
if __name__ == "__main__":
    unlock_zip()
