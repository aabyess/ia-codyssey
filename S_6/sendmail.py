from __future__ import annotations

import argparse
import csv
import getpass
import mimetypes
import os
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path
from smtplib import SMTP, SMTPAuthenticationError
from typing import List, Tuple

# =========================
# SMTP 서비스 정보
# =========================
SMTP_PRESETS = {
    'gmail': ('smtp.gmail.com', 587, 'Gmail STARTTLS (앱 비밀번호 권장)'),
    'naver': ('smtp.naver.com', 587, 'Naver STARTTLS (앱 비밀번호 권장)'),
}

DEFAULT_SENDER = 'h00411@naver.com'
DEFAULT_CSV = 'mail_target_list.csv'


# =========================
# CSV 읽기
# =========================
def read_recipients(csv_path: str) -> List[Tuple[str, str]]:
    """CSV 파일에서 (이름, 이메일) 목록을 읽어 리스트로 반환"""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f'CSV 파일을 찾을 수 없습니다: {csv_path}')

    recipients: List[Tuple[str, str]] = []
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return recipients

    # 첫 줄을 헤더로 간주
    data_rows = rows[1:] if len(rows) > 1 else []

    for row in data_rows:
        if len(row) < 2:
            continue
        name = row[0].strip()
        email = row[1].strip()
        if email:
            recipients.append((name, email))
    return recipients


# =========================
# 메일 메시지 작성
# =========================
def build_message(sender: str, to_list: List[str], subject: str,
                  text_body: str | None, html_body: str | None) -> EmailMessage:
    """HTML 및 텍스트 본문을 포함한 EmailMessage 생성"""
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = ', '.join(to_list)
    msg['Subject'] = subject

    if text_body:
        msg.set_content(text_body)
    else:
        msg.set_content('This email contains HTML content.')

    if html_body:
        msg.add_alternative(html_body, subtype='html')

    return msg


def attach_inline_images(msg: EmailMessage, image_paths: List[str]) -> None:
    """
    HTML 파트에 inline 이미지(Related)로 첨부하고 CID는 img1, img2, ... 로 부여.
    HTML 본문이 없으면 첨부하지 않음.
    """
    if not image_paths:
        return

    # HTML 파트가 없으면 inline 첨부 불가
    payload = msg.get_payload()
    if not isinstance(payload, list) or len(payload) < 2:
        # HTML이 없는 경우는 조용히 리턴(또는 필요 시 예외)
        return

    # 마지막 파트를 HTML로 간주 (set_content -> text/plain, add_alternative -> text/html)
    html_part = payload[-1]

    for idx, image_path in enumerate(image_paths, start=1):
        p = Path(image_path)
        if not p.exists():
            raise FileNotFoundError(f'이미지 파일을 찾을 수 없습니다: {image_path}')

        ctype, encoding = mimetypes.guess_type(str(p))
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)

        with p.open('rb') as f:
            data = f.read()

        cid = f'img{idx}'
        # EmailMessage.add_related는 EmailMessage 3.11+ 에서 제공.
        # 하위 호환을 위해 html_part.get_payload().append() 대신 메시지 API 사용.
        html_part.add_related(data, maintype=maintype, subtype=subtype, cid=f'<{cid}>')
        # 사용자는 HTML에서 <img src="cid:img1"> 로 참조


# =========================
# SMTP 연결
# =========================
def open_smtp(service: str, sender: str) -> SMTP:
    """SMTP 서버 연결 및 로그인"""
    if service not in SMTP_PRESETS:
        raise ValueError('지원되지 않는 서비스입니다. gmail 또는 naver 중 선택하세요.')

    host, port, note = SMTP_PRESETS[service]
    print(f'[*] SMTP 연결 중... ({host}:{port}) - {note}')
    password = getpass.getpass(f'{sender} 계정의 앱 비밀번호를 입력하세요: ')

    context = ssl.create_default_context()
    server = SMTP(host, port, timeout=30)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    try:
        server.login(sender, password)
    except SMTPAuthenticationError:
        print('[ERROR] 로그인 실패! 비밀번호(앱 비밀번호)를 확인하세요.')
        server.quit()
        sys.exit(1)

    print('[OK] SMTP 로그인 성공')
    return server


# =========================
# 발송 모드
# =========================
def send_bulk(server: SMTP, sender: str, recipients: List[Tuple[str, str]],
              subject: str, text_body: str | None, html_body: str | None,
              images: List[str] | None) -> None:
    """bulk 모드: 여러 명을 To에 열거"""
    to_list = [email for _, email in recipients]
    subj = subject.replace('{name}', '')
    html = (html_body or '').replace('{name}', '')
    msg = build_message(sender, to_list, subj, text_body, html)
    if images:
        attach_inline_images(msg, images)
    server.send_message(msg)
    print(f'[OK] bulk 발송 완료 ({len(to_list)}명)')


def send_single(server: SMTP, sender: str, recipients: List[Tuple[str, str]],
                subject: str, text_body: str | None, html_body: str | None,
                images: List[str] | None) -> None:
    """single 모드: 개인별 메일 발송"""
    for name, email in recipients:
        subj = subject.replace('{name}', name)
        html = html_body.replace('{name}', name) if html_body else None
        msg = build_message(sender, [email], subj, text_body, html)
        if images:
            attach_inline_images(msg, images)
        server.send_message(msg)
        print(f'[OK] {name} <{email}> 메일 전송 완료')
    print(f'[OK] 총 {len(recipients)}명에게 발송 완료')


# =========================
# CLI 인자
# =========================
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='CSV 목록을 읽어 HTML 메일을 발송합니다.')
    parser.add_argument('--service', choices=['gmail', 'naver'], default='naver', help='SMTP 서비스 선택')
    parser.add_argument('--sender', default=DEFAULT_SENDER, help='보내는 사람 이메일 주소')
    parser.add_argument('--subject', required=True, help='메일 제목 (예: "안내: {name}님")')
    parser.add_argument('--body', help='텍스트 본문')
    parser.add_argument('--html', help='HTML 본문 문자열')
    parser.add_argument('--html-file', help='HTML 파일 경로')
    parser.add_argument('--csv', default=DEFAULT_CSV, help='수신자 CSV 파일 (기본: mail_target_list.csv)')
    parser.add_argument('--mode', choices=['bulk', 'single'], default='single',
                        help='bulk: 한 통 / single: 개인별 (기본)')
    parser.add_argument('--image', nargs='*',
                        help='HTML에 inline으로 붙일 이미지 파일 경로들 (CID는 img1, img2, ...로 자동 부여)')
    return parser.parse_args()


# =========================
# 메인 함수
# =========================
def main() -> None:
    args = parse_args()

    # CSV 읽기
    try:
        recipients = read_recipients(args.csv)
    except FileNotFoundError as e:
        print(f'[ERROR] {e}')
        sys.exit(1)

    if not recipients:
        print('[WARN] CSV 파일에 유효한 수신자가 없습니다.')
        sys.exit(1)

    # 본문 준비
    html_body = None
    if args.html_file:
        path = Path(args.html_file)
        if not path.exists():
            print(f'[ERROR] HTML 파일을 찾을 수 없습니다: {args.html_file}')
            sys.exit(1)
        html_body = path.read_text(encoding='utf-8')
    elif args.html:
        html_body = args.html

    text_body = args.body or None

    # SMTP 연결
    server = open_smtp(args.service, args.sender)

    try:
        if args.mode == 'bulk':
            send_bulk(server, args.sender, recipients, args.subject, text_body, html_body, args.image)
        else:
            send_single(server, args.sender, recipients, args.subject, text_body, html_body, args.image)
    finally:
        server.quit()
        print('[*] SMTP 세션 종료')


if __name__ == '__main__':
    main()
