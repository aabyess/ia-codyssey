# Caesar Cipher를 이용해 암호화된 텍스트를 모든 가능한 경우로 복호화하는 함수
def caesar_cipher_decode(target_text):
    decoded_results = []  # 복호화된 결과를 저장할 리스트 생성

    # 시프트 값(0~25)만큼 반복하며 모든 가능한 복호화 시도
    for shift in range(26):
        decoded_text = ''  # 현재 시프트 값에 대한 복호화 결과를 저장할 문자열
        
        # 입력 텍스트의 각 문자별로 처리
        for char in target_text:
            if char.isalpha():  # 알파벳인 경우에만 처리
                start = ord('A') if char.isupper() else ord('a')  # 대소문자 구분하여 시작점 설정
                # 시프트 연산 후 알파벳 범위(26글자) 내로 유지
                decoded_char = chr(start + (ord(char) - start - shift) % 26)
                decoded_text += decoded_char  # 복호화된 문자 추가
            else:
                decoded_text += char  # 알파벳 외 문자는 그대로 추가

        decoded_results.append((shift, decoded_text))  # 결과 리스트에 추가
        print(f'Shift={shift}: {decoded_text}')  # 각 결과 출력

    return decoded_results  # 모든 복호화 결과 반환

# 예시로 사용할 간단한 영어 단어 사전을 로드하는 함수
def load_dictionary():
    # 유의미한 단어 목록
    return {'emergency', 'storage', 'key', 'mars', 'caesar', 'password', 'open', 'door'}

# 복호화된 결과 중에서 실제 영어 단어를 포함한 암호를 찾아내는 함수
def identify_password(decoded_results, dictionary):
    # 각 복호화된 결과를 검사
    for shift, text in decoded_results:
        words = text.lower().split()  # 소문자로 변환 후 단어로 분리
        # 사전의 단어가 포함된 결과를 발견하면 성공 메시지 출력 후 반환
        if any(word in dictionary for word in words):
            print(f'해독 성공: Shift {shift} -> {text}')
            return shift, text
    # 사전에 있는 단어가 없으면 None 반환
    return None, None

# 실제 프로그램 실행부 (메인 로직)
try:
    # 암호화된 텍스트가 저장된 파일 읽기 시도
    with open('password.txt', 'r') as file:
        encrypted_text = file.read().strip()  # 파일 내용을 읽고 공백 제거
except FileNotFoundError:
    # 파일이 존재하지 않을 때 오류 메시지 출력
    print('Error: password.txt 파일을 찾을 수 없습니다.')
    exit()  # 프로그램 종료
except Exception as e:
    # 그 외의 오류 발생 시 메시지 출력 후 종료
    print(f'파일 읽기 중 오류가 발생했습니다: {e}')
    exit()

# 단어 사전 로드
dictionary = load_dictionary()

# Caesar Cipher를 이용한 모든 가능한 복호화 결과 생성
decoded_results = caesar_cipher_decode(encrypted_text)

# 생성된 결과 중 실제 암호 찾기 시도
shift, final_password = identify_password(decoded_results, dictionary)

# 성공적으로 암호를 찾았을 경우 결과를 파일에 저장
if shift is not None:
    try:
        with open('result.txt', 'w') as file:
            file.write(final_password)
        print(f'최종 암호가 result.txt에 저장되었습니다. (Shift={shift})')
    except Exception as e:
        print(f'파일 저장 중 오류가 발생했습니다: {e}')
else:
    # 암호를 찾지 못한 경우 메시지 출력
    print('적합한 암호를 찾지 못했습니다.')


#0521