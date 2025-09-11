
import socket
import threading
from typing import Dict, Tuple


class ChatServer:
    """멀티스레드 TCP 채팅 서버."""

    def __init__(self, host: str = '0.0.0.0', port: int = 5000) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET + SOCK_STREAM → TCP 소켓.
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # SO_REUSEADDR로 재시작 시 포트 재사용.
        # 접속 사용자 등록부: 사용자명 -> (소켓, 주소)
        self.clients: Dict[str, Tuple[socket.socket, Tuple[str, int]]] = {}
        self.clients_lock = threading.Lock()

        self.running = False

    def start(self) -> None:
        """서버 시작."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen() # bind/listen으로 서버 대기 진입.
        self.server_socket.settimeout(1.0) #  accept() 블로킹 방지용 타임아웃(1초)
        self.running = True
        print(f'[INFO] 채팅서버 시작! {self.host}:{self.port}')

        try:
            """여러 명 동시 통신(멀티스레드)"""
            while self.running:
                client_sock, addr = self.server_socket.accept()
                t = threading.Thread(
                    target=self._handle_client, # 클라이언트 접속마다 새 스레드 생성 → _handle_client()에서 독립 처리.
                    args=(client_sock, addr),
                    daemon=True,
                    # 데몬 스레드: 메인 종료 시 자동 종료
                )
                t.start()
        except KeyboardInterrupt:
            print('\n[INFO] KeyboardInterrupt: shutting down...')
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """서버 종료."""
        self.running = False
        with self.clients_lock:
            for username, (sock, _) in list(self.clients.items()):
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                sock.close()
            self.clients.clear()
        try:
            self.server_socket.close()
        except OSError:
            pass
        print('[INFO] Server closed.')

    def _handle_client(self, client_sock: socket.socket, addr: Tuple[str, int]) -> None:
        """클라이언트 연결 처리."""
        client_sock.sendall('안녕하세요! 사용자 이름을 입력해 주세요: '.encode('utf-8'))
        username = self._receive_valid_username(client_sock)
        if not username:
            self._safe_close(client_sock)
            return
        """입장 안내 브로드캐스트"""
        with self.clients_lock:
            self.clients[username] = (client_sock, addr)

        self._broadcast(f'-- {username} 님이 입장하셨습니다. --', exclude=None)

        try:
            while True:
                data = client_sock.recv(4096)
                if not data:
                    # 소켓이 끊어진 경우
                    break

                msg = data.decode('utf-8', errors='ignore').strip()
                if not msg:
                    continue

                # 종료 명령
                if msg == '/종료':
                    self._send_line(client_sock, '서버와의 연결을 종료합니다.')
                    break

                # ======= 보너스 과제: 귓속말 기능 구현 =======
                # 사용법 1) /귓속말 대상유저 메시지...
                # 사용법 2) /w 대상유저 메시지...
                if msg.startswith('/귓속말 ') or msg.startswith('/w '):
                    self._handle_whisper(username, msg, client_sock)
                    continue
                # ===========================================

                # 일반 메시지 브로드캐스트
                formatted = f'{username}> {msg}'
                self._broadcast(formatted, exclude=None)
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            # 무시하고 정리 루틴으로 진행
            pass
        finally:
            self._cleanup_user(username)

    def _receive_valid_username(self, client_sock: socket.socket) -> str:
        """중복되지 않는 올바른 사용자명을 수신."""
        while True:
            data = client_sock.recv(4096)
            if not data:
                return ''
            candidate = data.decode('utf-8', errors='ignore').strip()

            if not candidate:
                self._send_line(client_sock, '공백은 이름으로 사용할 수 없습니다. 다시 입력해 주세요: ')
                continue

            if ' ' in candidate:
                self._send_line(client_sock, '이름에는 공백을 포함할 수 없습니다. 다시 입력해 주세요: ')
                continue

            with self.clients_lock:
                if candidate in self.clients:
                    self._send_line(client_sock, '이미 사용 중인 이름입니다. 다른 이름을 입력해 주세요: ')
                    continue

            # 고유 이름 확보
            self._send_line(client_sock, f'환영합니다, {candidate}님! 채팅에 참여하였습니다.')
            return candidate

    def _handle_whisper(self, sender: str, raw: str, client_sock: socket.socket) -> None:
        """보너스 과제: 귓속말 처리."""
        # 포맷 통일: '/귓속말 ' 또는 '/w ' 제거
        if raw.startswith('/귓속말 '):
            content = raw[len('/귓속말 '):].strip()
        else:
            content = raw[len('/w '):].strip()

        if not content:
            self._send_line(client_sock, '사용법: /귓속말 대상사용자 메시지  또는  /w 대상사용자 메시지')
            return

        # 첫 토큰은 대상 사용자, 나머지는 메시지
        parts = content.split(' ', 1)
        if len(parts) < 2:
            self._send_line(client_sock, '사용법: /귓속말 대상사용자 메시지  또는  /w 대상사용자 메시지')
            return

        target_user, message = parts[0].strip(), parts[1].strip()
        if not target_user or not message:
            self._send_line(client_sock, '대상 사용자와 메시지를 정확히 입력해 주세요.')
            return

        with self.clients_lock:
            target_entry = self.clients.get(target_user)

        if not target_entry:
            self._send_line(client_sock, f'[{target_user}] 사용자를 찾을 수 없습니다.')
            return

        target_sock, _ = target_entry
        whisper_to_target = f'(귓속말) {sender}> {message}'
        whisper_to_sender = f'(귓속말 전송됨) {sender} -> {target_user}: {message}'

        self._send_line(target_sock, whisper_to_target)
        self._send_line(client_sock, whisper_to_sender)

    def _broadcast(self, line: str, exclude: str = None) -> None:
        """모든 클라이언트에게 메시지 전파."""
        to_remove = []
        with self.clients_lock:
            for username, (sock, _) in self.clients.items():
                if exclude and username == exclude:
                    continue
                try:
                    sock.sendall((line + '\n').encode('utf-8'))
                except (BrokenPipeError, OSError):
                    to_remove.append(username)

            # 전송 실패한 소켓 정리
            for username in to_remove:
                entry = self.clients.pop(username, None)
                if entry:
                    try:
                        entry[0].close()
                    except OSError:
                        pass

    def _send_line(self, sock: socket.socket, line: str) -> None:
        """단일 소켓에 한 줄 전송."""
        try:
            sock.sendall((line + '\n').encode('utf-8'))
        except OSError:
            pass

    def _cleanup_user(self, username: str) -> None:
        """사용자 퇴장 처리 및 브로드캐스트."""
        with self.clients_lock:
            entry = self.clients.pop(username, None)

        if entry:
            sock, _ = entry
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass

            self._broadcast(f'-- {username} 님이 퇴장하셨습니다. --', exclude=None)


def main() -> None:
    server = ChatServer(host='0.0.0.0', port=5000)
    server.start()


if __name__ == '__main__':
    main()
