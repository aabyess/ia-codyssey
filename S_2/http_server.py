import json #JSON 형식 문자열 ↔ 파이썬 dict 변환에 사용.
import socket
import threading
from datetime import datetime #날짜와 시간 관련 고수준 객체.
from typing import Optional
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler #ThreadingHTTPServer로 동시 요청 처리(브라우저 다수 탭/기기 접속 대응)
from urllib.request import urlopen, Request #GeoIP 조회에서 사용
from urllib.error import URLError, HTTPError #여기서는 geolocate_ip에서 외부 API 호출이 실패했을 때 예외를 잡아 서버가 죽지 않게 처리

HOST = '0.0.0.0'
PORT = 8080

# 보너스 과제: 접속 IP의 위치 정보
ENABLE_GEOIP = True          # 위치 정보 조회 on/off
GEOIP_TIMEOUT = 1.5          # 조회 타임아웃(초)
GEOIP_ENDPOINT = 'https://ipinfo.io/{ip}/json'  # 간단하고 응답 빠른 공개 엔드포인트

def geolocate_ip(ip: str) -> Optional[str]:
    """보너스 과제: IP → 'City, Region, Country' 문자열 반환.
    외부 네트워크가 차단되어도 서버는 정상 동작해야 하므로 예외는 모두 흡수.
    """
    if not ENABLE_GEOIP:
        return None

    try:
        # 요청 URL 생성
        url = GEOIP_ENDPOINT.format(ip=ip)
        req = Request(url, headers={'User-Agent': 'Python-GeoIP/1.0'})
        # API 호출 및 응답 읽기
        with urlopen(req, timeout=GEOIP_TIMEOUT) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
        # "city", "region", "country" 값
        city = data.get('city') or ''
        region = data.get('region') or ''
        country = data.get('country') or ''
        # city, region, country 중 값이 있는 것만 리스트에 모음
        parts = [p for p in (city, region, country) if p]
        return ', '.join(parts) if parts else None
    # 서버는 절대 죽지 않고, 실패 시 그냥 위치를 알 수 없는 것으로 처리.
    except (URLError, HTTPError, TimeoutError, socket.timeout, ValueError):
        return None


class RequestStats:
    """
    역할: 서버가 처리한 요청 수를 세는 클래스
    여러 클라이언트가 동시에 접속해도 카운터 값이 꼬이지않게 """
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._count = 0

    def inc(self) -> int:
        with self._lock:
            self._count += 1
            return self._count


STATS = RequestStats()


class TestHandler(SimpleHTTPRequestHandler):
    """요청 처리 핸들러.
    - 파이썬 내장 HTTP 서버에서 정적 파일을 서빙하는 기본 핸들러.
    - `/` 또는 `/index.html`: index.html 파일을 읽어 응답
    - 그 외 경로: 정적 파일 서빙
    - 매 요청마다: 접속 시간, IP, 상태 코드, User-Agent, 요청 수 출력
    - GeoIP 조회 결과도 로그에 추가
    """

    server_version = 'TestHTTP/1.0'

    def do_GET(self) -> None:
        total = STATS.inc() # 요청 카운터 증가 
        client_ip = self.client_address[0] if self.client_address else '-' # 접속한 클라이언트의 IP
        ua = self.headers.get('User-Agent', '-') # 요청 헤더의 User-Agent
        path = self.path # 요청 URL 경로
        geo = geolocate_ip(client_ip) # 보너스: GeoIP 조회

        if path in ('/', '/index.html'): #index.html 파일이 있으면 읽어서 200 OK 응답.
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
                body = '<h1>404 Not Found</h1><p>index.html을 찾을 수 없습니다.</p>'.encode('utf-8')
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                code = 404
        else:
            try:
                super().do_GET()
                code = 200
            except Exception:
                self.send_error(500, 'Internal Server Error')
                code = 500

        # 콘솔 로그 출력
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base = (
            f'[ACCESS] time={now} ip={client_ip} path="{path}" '
            f'status={code} ua="{ua}" total={total}'
        )
        if geo:
            base += f' geo="{geo}"'
        print(base)

    def log_message(self, fmt: str, *args) -> None:
        
        return


def run_server() -> None: #서버 실행 함수
    httpd = ThreadingHTTPServer((HOST, PORT), TestHandler) # 요청마다 스레드를 새로 만들어 동시 처리 가능. 
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