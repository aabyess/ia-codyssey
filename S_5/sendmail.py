import smtplib
from email.mime.text import MIMEText

# 1. 계정/메일 정보 설정
sender = 'maeguming0000@gmail.com'     # Gmail 계정
password = '' # Gmail 앱 비밀번호      # 비밀번호
receiver = 'h00411@naver.com'          # 수신자 이메일
subject = 'SMTP 메일 전송 테스트'      # 제목
body = '안녕하세요. Python SMTP 테스트 메일입니다.'  # 본문

# 2. 메시지 객체 생성
msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = sender
msg['To'] = receiver

# 3. SMTP 서버 연결 및 메일 전송
with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.ehlo()
    server.starttls()
    server.login(sender, '앱비밀번호')  # Gmail 앱 비밀번호 사용
    server.send_message(msg)

print('메일 전송 완료!')
