import argparse # 명령행 인자(argument) 처리용 표준 라이브러리
import getpass # 밀번호를 화면에 표시하지 않고 입력받는 라이브러리
import mimetypes # mimetypes.guess_type('report.pdf') → 'application/pdf' 메일이 첨부 형식에 맞게 전송되도록 돕는다.
import os
import socket
import ssl #보안(암호화) 연결을 위한 라이브러리
import sys #프로그램 종료나 에러 메시지 출력 제어
from email.message import EmailMessage #메일 본문(헤더 + 내용 + 첨부 포함) 객체 생성 클래스
from smtplib import SMTP, SMTPAuthenticationError, SMTPConnectError, SMTPException, SMTPServerDisconnected #SMTP 서버 연결과 예외 처리용 클래스들

SMTP_HOST = 'smtp.gmail.com' #Gmail SMTP 서버 주소
SMTP_PORT = 587  # STARTTLS 권장 포트

# 이메일 메시지 객체 생성 함수
def build_message(sender: str, to_list: list[str], subject: str, body: str, attachments: list[str] | None) -> EmailMessage:
    """제목/본문/수신자/첨부를 포함한 EmailMessage 생성."""
    msg = EmailMessage() #비어 있는 이메일 컨테이너 생성
    msg['From'] = sender #보내는 사람
    msg['To'] = ', '.join(to_list)  #받는 사람(리스트를 문자열로 변환)
    msg['Subject'] = subject #제목
    msg.set_content(body) #본문

    if attachments: #첨부파일이 있으면
        for path in attachments: #첨부파일 경로들을 하나씩 처리
            try:
                ctype, encoding = mimetypes.guess_type(path) #파일 형식과 인코딩을 추측
                if ctype is None or encoding is not None: #추측 실패 시
                    ctype = 'application/octet-stream' #일반적인 바이너리 스트림 형식으로 지정
                maintype, subtype = ctype.split('/', 1) #메인 타입과 서브타입 분리

                with open(path, 'rb') as f: #첨부파일을 바이너리 모드로 읽기
                    data = f.read() # 파일 내용 읽기

                filename = os.path.basename(path) #파일 이름 추출
                msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename) # 첨부파일 추가
            except FileNotFoundError:
                raise FileNotFoundError(f'첨부 파일을 찾을 수 없습니다: {path}')
            except PermissionError:
                raise PermissionError(f'첨부 파일에 접근 권한이 없습니다: {path}')
            except OSError as exc:
                raise OSError(f'첨부 파일 처리 중 오류: {path} ({exc})') from exc

    return msg #완성된 이메일 메시지 객체 반환

# 실제로 메일을 보내는 함수
def send_email(sender: str, app_password: str, to_list: list[str], subject: str, body: str, attachments: list[str] | None) -> None:
    """Gmail SMTP로 메일 전송."""
    msg = build_message(sender, to_list, subject, body, attachments) #이메일 메시지 객체 생성

    context = ssl.create_default_context() #기본 SSL 컨텍스트 생성
    try:
        with SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server: #SMTP 서버에 연결 (20초 타임아웃)
            server.ehlo() #서버 인사 (확인)
            server.starttls(context=context) #보안 연결 시작
            server.ehlo() #다시 인사
            server.login(sender, app_password)  #로그인 (앱 비밀번호 사용)
            server.send_message(msg) #메일 전송
    except SMTPAuthenticationError: 
        raise SMTPAuthenticationError(535, '인증 실패: 앱 비밀번호(16자리) 또는 2단계 인증 설정을 확인하세요.')
    except SMTPConnectError:
        raise ConnectionError('SMTP 서버에 연결하지 못했습니다. 호스트/포트 또는 네트워크 상태를 확인하세요.')
    except SMTPServerDisconnected:
        raise ConnectionError('SMTP 서버와의 연결이 예기치 않게 종료되었습니다. 다시 시도하세요.')
    except (socket.timeout, socket.gaierror) as exc:
        raise ConnectionError(f'네트워크 오류: {exc}') from exc
    except SMTPException as exc:
        raise RuntimeError(f'SMTP 오류: {exc}') from exc

# 명령행 인자 처리 함수
# 터미널에서 입력된 명령어(옵션들)를 읽어서 변수로 정리하는 역할
def parse_args() -> argparse.Namespace: #명령행 인자 처리
    parser = argparse.ArgumentParser(description='Gmail SMTP로 메일 보내기 (첨부 지원, 표준 라이브러리만).') #프로그램 설명
    parser.add_argument('--sender', default='maeguming0000@gmail.com', help='보내는 사람 이메일') #보내는 사람 이메일
    parser.add_argument('--to', nargs='+', default=['h00411@naver.com'], help='받는 사람 이메일(여러 명 가능)') #받는 사람 이메일(여러 명 가능)
    parser.add_argument('--subject', default='SMTP 메일 전송 테스트', help='메일 제목') #메일 제목 
    parser.add_argument('--body', default='안녕하세요. Python SMTP 테스트 메일입니다.', help='메일 본문') #메일 본문
    parser.add_argument('--attach', nargs='*', default=None, help='첨부 파일 경로들 (옵션)') #첨부 파일 경로들 (옵션)
    return parser.parse_args() #파싱된 인자 반환

def main() -> None:
    args = parse_args() #명령행 인자 파싱
    # “파싱(parsing)”이라는 말은 쉽게 말하면 문자열을 해석해서 의미 있는 데이터로 나누는 과정
    # 예를 들어, '--to' 옵션에 'h00411@naver.com'이라는 문자열이 주어지면, 이를 리스트 형태로 변환하여 args.to에 저장

    # 앱 비밀번호는 실행 시 안전 입력
    app_pw = getpass.getpass('Gmail 앱 비밀번호(16자리)를 입력하세요: ').strip()

    if len(app_pw.replace(' ', '')) < 16: #앱 비밀번호 길이 검사 (공백 제거 후 16자리 미만)
        print('오류: 앱 비밀번호가 올바르지 않습니다. Google 계정에서 앱 비밀번호(16자리)를 발급받으세요.', file=sys.stderr)
        sys.exit(1) #비정상 종료 코드 1

    try:
        send_email( #이메일 전송 함수 호출
            sender=args.sender, # 보내는 사람 이메일
            app_password=app_pw, # 앱 비밀번호
            to_list=args.to, # 받는 사람 이메일 리스트 
            subject=args.subject, # 메일 제목
            body=args.body, # 메일 본문 
            attachments=args.attach, # 첨부 파일 경로 리스트 (없을 수도 있음)
        )
        print(' 메일 전송 성공')
    except Exception as exc:
        print(f' 메일 전송 실패: {exc}', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
