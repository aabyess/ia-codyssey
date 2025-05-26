import os
import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
import glob
import csv

import speech_recognition as sr  # STT를 위한 라이브러리
from pydub import AudioSegment   # wav/mp3 변환 지원 (STT 처리용)

RECORD_FOLDER = 'records'
os.makedirs(RECORD_FOLDER, exist_ok=True)

# 1. 음성 녹음 함수
def record_voice(duration=10, sample_rate=44100):
    print(f"{duration}초간 녹음 시작...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()

    filename = datetime.now().strftime("%Y%m%d-%H%M%S") + ".wav"
    filepath = os.path.join(RECORD_FOLDER, filename)
    write(filepath, sample_rate, audio_data)
    print(f"녹음 완료! 저장 위치: {filepath}")
    return filepath

# 2. 날짜 범위에 따른 파일 목록 검색 (보너스)
def list_records_by_date(start_date, end_date):
    print(f" 녹음 파일 검색: {start_date} ~ {end_date}")
    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")

    matched_files = []
    for filepath in glob.glob(os.path.join(RECORD_FOLDER, "*.wav")):
        filename = os.path.basename(filepath)
        try:
            file_dt = datetime.strptime(filename[:8], "%Y%m%d")
            if start_dt <= file_dt <= end_dt:
                matched_files.append(filename)
        except:
            continue

    if matched_files:
        print(" 검색된 녹음 파일 목록:")
        for f in sorted(matched_files):
            print(f" - {f}")
    else:
        print(" 해당 기간에 녹음 파일이 없습니다.")

# 3. STT 실행 함수: 음성을 텍스트로 변환하여 CSV 저장
def transcribe_audio_to_csv(wav_path):
    print(f"[🔍] STT 처리 중: {wav_path}")
    recognizer = sr.Recognizer()

    audio = AudioSegment.from_wav(wav_path)  # wav 파일 로드
    duration_sec = len(audio) / 1000         # 전체 길이 (초)

    # 10초씩 나눠서 인식 (길이 제한 회피)
    chunk_length = 10
    base_filename = os.path.splitext(os.path.basename(wav_path))[0]
    csv_path = os.path.join(RECORD_FOLDER, base_filename + ".csv")

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["시작시간(초)", "인식된 텍스트"])

        for i in range(0, int(duration_sec), chunk_length):
            chunk = audio[i*1000:(i+chunk_length)*1000]  # 밀리초 단위
            chunk.export("temp.wav", format="wav")       # 임시 저장

            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language='ko-KR')
                    writer.writerow([i, text])
                    print(f" {i}초 ~ {i+chunk_length}초: {text}")
                except sr.UnknownValueError:
                    print(f" {i}초 ~ {i+chunk_length}초: 인식 실패")
                    writer.writerow([i, "(인식 실패)"])
                except sr.RequestError as e:
                    print(f" 오류 발생: {e}")
                    break

    os.remove("temp.wav")
    print(f" CSV 저장 완료: {csv_path}")

# 4. 보너스: 키워드로 CSV 파일 내 검색
def search_keyword_in_transcripts(keyword):
    print(f" 키워드 검색: \"{keyword}\"")
    results = []

    for csv_file in glob.glob(os.path.join(RECORD_FOLDER, "*.csv")):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더 건너뜀
            for row in reader:
                if keyword in row[1]:
                    results.append((os.path.basename(csv_file), row[0], row[1]))

    if results:
        print("[🔎] 검색 결과:")
        for file, time, text in results:
            print(f"📄 {file} | ⏱️ {time}초 | 🗣️ {text}")
    else:
        print("키워드를 포함하는 텍스트를 찾을 수 없습니다.")

# 메인 메뉴
if __name__ == "__main__":
    while True:
        print("\n=== Javis 음성 기록 시스템 ===")
        print("1. 새 음성 녹음")
        print("2. 날짜 범위로 녹음 파일 조회")
        print("3. 녹음 파일 → 텍스트 변환(STT + CSV 저장)")
        print("4. 키워드로 기록 검색 (CSV 내)")
        print("0. 종료")
        choice = input("선택 >> ")

        if choice == "1":
            try:
                sec = int(input("녹음 시간 (초): "))
                record_voice(duration=sec)
            except:
                print("[오류] 숫자로 입력해 주세요.")
        elif choice == "2":
            s = input("시작 날짜 (예: 20240501): ")
            e = input("종료 날짜 (예: 20240531): ")
            list_records_by_date(s, e)
        elif choice == "3":
            f = input("변환할 wav 파일명 (예: 20240526-193000.wav): ")
            full_path = os.path.join(RECORD_FOLDER, f)
            if os.path.exists(full_path):
                transcribe_audio_to_csv(full_path)
            else:
                print(" 해당 파일이 존재하지 않습니다.")
        elif choice == "4":
            keyword = input("검색할 키워드: ")
            search_keyword_in_transcripts(keyword)
        elif choice == "0":
            break
        else:
            print("잘못된 선택입니다.")
