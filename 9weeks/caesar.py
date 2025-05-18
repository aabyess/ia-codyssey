def caesar_cipher_decode(target_text):
    decoded_results = []

    for shift in range(26):
        decoded_text = ''
        for char in target_text:
            if char.isalpha():
                start = ord('A') if char.isupper() else ord('a')
                decoded_char = chr(start + (ord(char) - start - shift) % 26)
                decoded_text += decoded_char
            else:
                decoded_text += char
        decoded_results.append((shift, decoded_text))
        print(f'Shift={shift}: {decoded_text}')

    return decoded_results

# 간단한 영어 단어 사전으로 예시 작성
def load_dictionary():
    return {'emergency', 'storage', 'key', 'mars', 'caesar', 'password', 'open', 'door'}

# 사전과 비교하여 암호를 자동으로 식별
def identify_password(decoded_results, dictionary):
    for shift, text in decoded_results:
        words = text.lower().split()
        if any(word in dictionary for word in words):
            print(f'해독 성공: Shift {shift} -> {text}')
            return shift, text
    return None, None

# 메인 실행부
try:
    with open('password.txt', 'r') as file:
        encrypted_text = file.read().strip()
except FileNotFoundError:
    print('Error: password.txt 파일을 찾을 수 없습니다.')
    exit()
except Exception as e:
    print(f'파일 읽기 중 오류가 발생했습니다: {e}')
    exit()

dictionary = load_dictionary()
decoded_results = caesar_cipher_decode(encrypted_text)

shift, final_password = identify_password(decoded_results, dictionary)

if shift is not None:
    try:
        with open('result.txt', 'w') as file:
            file.write(final_password)
        print(f'최종 암호가 result.txt에 저장되었습니다. (Shift={shift})')
    except Exception as e:
        print(f'파일 저장 중 오류가 발생했습니다: {e}')
else:
    print('적합한 암호를 찾지 못했습니다.')
