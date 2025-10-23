# sendmail.py
import argparse
import csv
import getpass
import mimetypes
import os
import re
import socket
import ssl
import sys
import time
from email.message import EmailMessage
from smtplib import (
    SMTP, SMTPAuthenticationError, SMTPConnectError,
    SMTPException, SMTPServerDisconnected
)

# ───────────────── SMTP 기본값 ─────────────────
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587

# 이메일 형식 검사용 (간단 버전)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ───────────────── CSV 로더 ─────────────────
def read_targets_from_csv(path: str) -> list[dict]:
    """CSV(이름,이메일) → [{'name':..., 'email':...}, ...]"""
    targets: list[dict] = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV 헤더가 없습니다. 첫 줄에 '이름,이메일'이 있어야 합니다.")
        # 헤더 유연 대응
        name_key, email_key = None, None
        headers = [h.strip() for h in reader.fieldnames]
        for h in headers:
            low = h.lower()
            if name_key is None and low in ('이름', 'name'):
                name_key = h
            if email_key is None and low in ('이메일', 'email', 'e-mail'):
                email_key = h
        if not name_key or not email_key:
            raise ValueError("CSV 헤더에 '이름'과 '이메일' 열이 필요합니다.")
        # 행 로드
        for row in reader:
            name = (row.get(name_key) or '').strip()
            email = (row.get(email_key) or '').strip()
            if email and EMAIL_RE.match(email):
                targets.append({'name': name, 'email': email})
    if not targets:
        raise ValueError("CSV에서 유효한 수신자를 찾지 못했습니다.")
    return targets


# ───────────────── 본문/메시지 빌더 ─────────────────
def load_html(path: str | None) -> str | None:
    if not path:
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def build_message(
    sender: str,
    to_list: list[str],
    subject: str,
    text_body: str | None,
    html_body: str | None,
    attachments: list[str] | None
) -> EmailMessage:
    """멀티파트(텍스트+HTML) + 첨부파일"""
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = ', '.join(to_list)
    msg['Subject'] = subject

    fallback = text_body or "This email contains HTML content. Please use an HTML-capable viewer."
    if html_body:
        msg.set_content(fallback)                       # text/plain
        msg.add_alternative(html_body, subtype='html')  # text/html
    else:
        msg.set_content(fallback)

    if attachments:
        for path in attachments:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"첨부 파일을 찾을 수 없습니다: {path}")
            ctype, encoding = mimetypes.guess_type(path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            with open(path, 'rb') as f:
                data = f.read()
            filename = os.path.basename(path)
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)

    return msg


# ───────────────── 전송기 ─────────────────
def send_message(sender: str, app_password: str, msg: EmailMessage) -> None:
    """단일 메시지 전송"""
    context = ssl.create_default_context()
    try:
        with SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender, app_password)
            server.send_message(msg)
    except SMTPAuthenticationError:
        raise SMTPAuthenticationError(535, '인증 실패: 앱 비밀번호(16자리) 또는 2단계 인증을 확인하세요.')
    except SMTPConnectError:
        raise ConnectionError('SMTP 서버 연결 실패: 호스트/포트 또는 네트워크 상태를 확인하세요.')
    except SMTPServerDisconnected:
        raise ConnectionError('SMTP 서버 연결이 예기치 않게 종료되었습니다.')
    except (socket.timeout, socket.gaierror) as exc:
        raise ConnectionError(f'네트워크 오류: {exc}') from exc
    except SMTPException as exc:
        raise RuntimeError(f'SMTP 오류: {exc}') from exc


# ───────────────── CLI 옵션 ─────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Gmail SMTP로 HTML 메일 보내기 (CSV 명단 지원)')
    p.add_argument('--sender', required=True, help='보내는 사람 이메일 (예: you@gmail.com)')
    # 대상 지정: CSV가 있으면 CSV 우선, 없으면 --to 사용
    p.add_argument('--targets-csv', default='mail_target_list.csv', help='수신자 CSV 경로 (기본: mail_target_list.csv)')
    p.add_argument('--to', nargs='+', help='받는 사람 이메일(여러 명 가능). CSV 없을 때 사용')
    p.add_argument('--subject', required=True, help='메일 제목')
    p.add_argument('--body', help='텍스트 대체 본문(HTML이 안 보이는 경우용)')
    p.add_argument('--html', help='HTML 본문 문자열 직접 입력')
    p.add_argument('--html-file', help='HTML 본문 파일 경로 (예: mars_message.html)')
    p.add_argument('--attach', nargs='*', default=None, help='첨부 파일 경로들 (0개 이상)')
    p.add_argument('--mode', choices=['single', 'bulk'], default='single', help='single=개별 발송(추천), bulk=한 통에 다수')
    p.add_argument('--sleep', type=float, default=0.8, help='single 모드에서 발송 간 대기(초)')
    return p.parse_args()


# ───────────────── 메인 ─────────────────
def main():
    args = parse_args()

    # 본문 준비
    text_body = args.body or "HTML 메일입니다. HTML이 보이지 않으면 이 문장을 확인해 주세요."
    html_body = args.html or load_html(args.html_file)

    # 앱 비밀번호
    app_pw = getpass.getpass('Gmail 앱 비밀번호(16자리): ').strip()
    if len(app_pw.replace(' ', '')) < 16:
        print('오류: 앱 비밀번호가 올바르지 않습니다. 16자리 앱 비밀번호를 사용하세요.', file=sys.stderr)
        sys.exit(1)

    # 대상 수신자
    targets: list[dict]
    if args.targets_csv and os.path.exists(args.targets_csv):
        targets = read_targets_from_csv(args.targets_csv)
    elif args.to:
        # 이름 없이 이메일만
        cleaned = [t for t in args.to if EMAIL_RE.match(t)]
        if not cleaned:
            print('오류: 유효한 수신자 이메일이 없습니다.', file=sys.stderr)
            sys.exit(1)
        targets = [{'name': '', 'email': t} for t in cleaned]
    else:
        print("오류: --targets-csv 파일이 없고 --to 옵션도 없습니다.", file=sys.stderr)
        sys.exit(1)

    to_emails = [t['email'] for t in targets]

    try:
        if args.mode == 'bulk':
            # 한 통에 여러 명
            msg = build_message(
                sender=args.sender,
                to_list=to_emails,
                subject=args.subject,
                text_body=text_body,
                html_body=html_body,
                attachments=args.attach
            )
            send_message(args.sender, app_pw, msg)
            print(f'✅ BULK 전송 완료 ({len(to_emails)}명)')
        else:
            # 개별 발송
            sent = 0
            for t in targets:
                msg = build_message(
                    sender=args.sender,
                    to_list=[t['email']],
                    subject=args.subject,
                    text_body=text_body,
                    html_body=html_body,
                    attachments=args.attach
                )
                send_message(args.sender, app_pw, msg)
                print(f"OK ▶ {t['email']}")
                sent += 1
                if args.sleep > 0:
                    time.sleep(args.sleep)
            print(f'✅ SINGLE 전송 완료 ({sent}명)')
    except Exception as exc:
        print(f'메일 전송 실패: {exc}', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
