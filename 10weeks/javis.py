import os
import sounddevice as sd           # 마이크 입력 및 녹음용 라이브러리
from scipy.io.wavfile import write # 녹음된 데이터를 wav 파일로 저장
from datetime import datetime      # 현재 날짜와 시간을 처리하기 위한 모듈
import glob                        # 파일 탐색용 (날짜 범위 검색 시 활용)

# 녹음 파일 저장 폴더 생성
RECORD_FOLDER = 'records'                     # 저장 폴더명
os.makedirs(RECORD_FOLDER, exist_ok=True)     # 폴더가 없으면 새로 생성

# 음성 녹음 함수 정의
def record_voice(duration=10, sample_rate=44100):
    """
    시스템의 마이크를 통해 음성을 녹음하고
    지정된 폴더에 날짜/시간 형식으로 저장하는 함수
    :param duration: 녹음 시간 (초 단위)
    :param sample_rate: 오디오 샘플링 주기 (Hz, 기본 44.1kHz)
    """
    print(f"{duration}초간 녹음 시작...")
    
    # duration 초 동안 녹음 데이터를 수집 (모노 채널)
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()  # 녹음이 끝날 때까지 대기

    # 파일 이름 형식: '년월일-시간분초.wav'
    filename = datetime.now().strftime("%Y%m%d-%H%M%S") + ".wav"
    filepath = os.path.join(RECORD_FOLDER, filename)

    # 녹음된 데이터를 .wav 파일로 저장
    write(filepath, sample_rate, audio_data)

    print(f"녹음 완료! 저장 위치: {filepath}")
    return filepath  # 파일 경로 반환

# 날짜 범위에 따른 파일 조회 기능 (보너스 과제)
def list_records_by_date(start_date, end_date):
    """
    지정된 날짜 범위 내에 저장된 녹음 파일 목록을 출력하는 함수
    :param start_date: 시작 날짜 (형식: 'YYYYMMDD')
    :param end_date: 종료 날짜 (형식: 'YYYYMMDD')
    """
    print(f"녹음 파일 검색: {start_date} ~ {end_date}")
    
    # 입력된 문자열을 datetime 객체로 변환
    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")

    matched_files = []  # 조건에 맞는 파일들을 저장할 리스트

    # 모든 녹음 파일들을 순회하며 날짜 필터링
    for filepath in glob.glob(os.path.join(RECORD_FOLDER, "*.wav")):
        filename = os.path.basename(filepath)
        try:
            file_dt = datetime.strptime(filename[:8], "%Y%m%d")
            if start_dt <= file_dt <= end_dt:
                matched_files.append(filename)
        except:
            continue  # 날짜 파싱 실패 시 무시

    # 결과 출력
    if matched_files:
        print(" 해당 기간의 녹음 파일 목록:")
        for f in sorted(matched_files):
            print(f" - {f}")
    else:
        print("해당 기간에 해당하는 녹음 파일이 없습니다.")

# 실행 루틴: 메뉴 기반 동작
if __name__ == "__main__":
    while True:
        print("\n=== Javis 음성 기록 시스템 ===")
        print("1. 새 음성 녹음")
        print("2. 날짜 범위로 녹음 파일 조회")
        print("0. 종료")
        choice = input("선택 >> ")

        if choice == "1":
            try:
                sec = int(input("녹음 시간 (초): "))
                record_voice(duration=sec)
            except:
                print("[오류] 숫자로 입력해 주세요.")
        elif choice == "2":
            s = input("시작 날짜 (예: 20250501): ")
            e = input("종료 날짜 (예: 20250531): ")
            list_records_by_date(s, e)
        elif choice == "0":
            break
        else:
            print("잘못된 선택입니다.")
