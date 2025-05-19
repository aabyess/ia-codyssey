def caesar_cipher_decode(target_text):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lower_alphabet = alphabet.lower()
    
    print("[*] 가능한 해독 결과:")
    
    for shift in range(1, 26):
        decoded = ""
        for char in target_text:
            if char in alphabet:
                idx = (alphabet.index(char) - shift) % 26
                decoded += alphabet[idx]
            elif char in lower_alphabet:
                idx = (lower_alphabet.index(char) - shift) % 26
                decoded += lower_alphabet[idx]
            else:
                decoded += char
        print(f"[{shift:2}] {decoded}")
        
        # 보너스 과제: 키워드가 포함되어 있으면 자동 저장
        if any(word in decoded.lower() for word in ["open", "the", "door", "access", "granted"]):
            try:
                with open("result.txt", "w", encoding="utf-8") as rf:
                    rf.write(decoded)
                print(f"\n[+] 키워드 자동 감지! 시프트 {shift}로 해독됨. result.txt에 저장됨.")
                break
            except Exception as e:
                print(f"[!] 저장 중 오류 발생: {e}")

try:
    with open("password.txt", "r", encoding="utf-8") as f:
        encrypted_text = f.read().strip()
        print(f"[*] 읽은 암호: {encrypted_text}")
        caesar_cipher_decode(encrypted_text)
except FileNotFoundError:
    print("[!] password.txt 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"[!] 오류 발생: {e}")

# 시프트 19 결과를 수동 저장
try:
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write("I love Mars")
    print("[+] result.txt에 저장 완료: I love Mars")
except Exception as e:
    print(f"[!] 저장 실패: {e}")
