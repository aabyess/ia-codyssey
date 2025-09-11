# chat_client.py
import socket
import threading
import sys

def recv_loop(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            print(data.decode('utf-8'), end='')
        except OSError:
            break
    print('\n[클라이언트 종료]')
    sys.exit(0)

def main():
    host = '127.0.0.1'
    port = 5000
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    #  연결 직후 서버의 첫 안내문(사용자 이름 입력 프롬프트)을 먼저 받아서 보여줌
    s.settimeout(2.0)  # 첫 메시지 대기용(2초면 충분)
    try:
        first = s.recv(4096)
        if first:
            sys.stdout.write(first.decode('utf-8'))
            sys.stdout.flush()
    except OSError:
        pass
    finally:
        s.settimeout(None)  # 다시 블로킹 모드

    # 이후에는 수신 전용 스레드
    t = threading.Thread(target=recv_loop, args=(s,), daemon=True)
    t.start()

    try:
        while True:
            line = input()
            s.sendall((line + '\n').encode('utf-8'))
            if line.strip() == '/종료':
                break
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        s.close()

if __name__ == '__main__':
    main()
