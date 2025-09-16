import json
import time
import socket
import threading
from datetime import datetime
from typing import Optional
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

HOST = '0.0.0.0'
PORT = 8080

# ===== 보너스 과제 설정 =====
ENABLE_GEOIP = True          # 위치 정보 조회 on/off
GEOIP_TIMEOUT = 1.5          # 조회 타임아웃(초)
GEOIP_ENDPOINT = 'https://ipinfo.io/{ip}/json'  # 간단하고 응답 빠른 공개 엔드포인트
# ===========================


def is_private_ip(ip: str) -> bool:
    """사설/로컬 IP 여부 간단 판단."""
    return (
        ip.startswith('10.')
        or ip.startswith('127.')
        or ip.startswith('192.168.')
        or ip.startswith('172.')  # 172.16.0.0/12 대역 포함 간략 처리
        or ip in ('::1', 'localhost')
    )


def geolocate_ip(ip: str) -> Optional[str]:
    """보너스 과제: IP → 'City, Region, Country' 문자열 반환.
    - 사설 IP, 로컬 IP는 조회하지 않음.
    - 외부 네트워크가 차단되어도 서버는 정상 동작해야 하므로 예외는 모두 흡수."""
    if not ENABLE_GEOIP or is_private_ip(ip):
        return None

    try:
        url = GEOIP_ENDPOINT.format(ip=ip)
        req = Request(url, headers={'User-Agent': 'Python-GeoIP/1.0'})
        with urlopen(req, timeout=GEOIP_TIMEOUT) as resp:
            # 응답 본문을 JSON으로 파싱
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
        city = data.get('city') or ''
        region = data.get('region') or ''
        country = data.get('country') or ''
        parts = [p for p in (city, region, country) if p]
        return ', '.join(parts) if parts else None
    except (URLError, HTTPError, TimeoutError, socket.timeout, ValueError):
        return None


class RequestStats:
    """간단 요청 카운터(스레드 안전)."""
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._count = 0

    def inc(self) -> int:
        with self._lock:
            self._count += 1
            return self._count

    def get(self) -> int:
        with self._lock:
            return self._count


STATS = RequestStats()


class TestHandler(SimpleHTTPRequestHandler):
    """핸들러.

    - `/` 또는 `/index.html`: index.html 파일을 읽어 200 OK로 응답
    - 그 외 경로: SimpleHTTPRequestHandler 기본 정적 파일 서빙
    - 매 요청마다 접속 시간, IP, 경로, 상태코드, User-Agent, 누적 요청 수 출력
    - (보너스) 공인 IP라면 간단한 위치 정보 조회 후 로그에 추가
    """

    server_version = 'TestHTTP/1.0'  # 서버 식별자(선택)

    def do_GET(self) -> None:
        """GET 요청 처리."""
        total = STATS.inc()  # 요청 카운터 증가
        client_ip = self.client_address[0] if self.client_address else '-'
        ua = self.headers.get('User-Agent', '-')
        path = self.path

        # (보너스) IP → 위치 정보 조회
        geo = geolocate_ip(client_ip)

        if path in ('/', '/index.html'):
            # index.html 직접 서빙
            try:
                with open('index.html', 'rb') as f:
                    body = f.read()
                self.send_response(200)  # 200 OK
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                code = 200
            except FileNotFoundError:
                # 한글 문자열은 .encode('utf-8')로 바이트화
                body = '<h1>404 Not Found</h1><p>index.html을 찾을 수 없습니다.</p>'.encode('utf-8')
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                code = 404
        else:
            # 나머지는 정적 파일 기본 동작
            try:
                super().do_GET()
                # 정확한 코드 값은 부모 로그에 찍히지만, 여기선 성공 가정
                code = 200
            except Exception:
                self.send_error(500, 'Internal Server Error')
                code = 500

        # 콘솔 접근 로그
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base = (
            f'[ACCESS] time={now} ip={client_ip} path="{path}" '
            f'status={code} ua="{ua}" total={total}'
        )
        if geo:
            base += f' geo="{geo}"'  # 보너스: 위치 정보
        print(base)

    # 기본 noisy 로그를 숨기고, 필요한 경우만 위에서 출력
    def log_message(self, fmt: str, *args) -> None:
        return


def run_server() -> None:
    """스레드 처리 가능한 HTTP 서버 실행."""
    httpd = ThreadingHTTPServer((HOST, PORT), TestHandler)
    print(f'[INFO] HTTP server listening on http://127.0.0.1:{PORT}')
    print('[INFO] Press Ctrl+C to stop')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n[INFO] KeyboardInterrupt: shutting down...')
    finally:
        httpd.server_close()
        print('[INFO] Server closed.')


if __name__ == '__main__':
    run_server()
