import os
import csv
import subprocess
import speech_recognition as sr

# ✅ WAV 파일을 PCM 형식으로 변환하는 함수
def convert_to_pcm_wav(input_path, output_path):
    command = [
        'ffmpeg', '-y', '-i', input_path,
        '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', output_path
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 🎙️ PCM WAV 오디오 파일을 텍스트로 변환하는 함수
def convert_audio_to_text(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data, language='ko-KR')
        except sr.UnknownValueError:
            return '인식 실패'
        except sr.RequestError:
            return 'API 오류'

# 💾 변환된 텍스트를 CSV 파일로 저장하는 함수
def save_text_to_csv(wav_file):
    base_name = os.path.splitext(wav_file)[0]
    wav_path = os.path.join('records', wav_file)
    converted_path = os.path.join('records', f'{base_name}_converted.wav')
    csv_path = os.path.join('records', f'{base_name}.csv')

    # PCM 변환
    convert_to_pcm_wav(wav_path, converted_path)

    # 변환된 PCM WAV로 텍스트 추출
    text = convert_audio_to_text(converted_path)

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['시간', '텍스트'])
        writer.writerow(['00:00', text])

    print(f'{csv_path} 저장 완료.')

# 🧹 records 폴더 내 모든 WAV 처리
def process_all_wav_files():
    folder = 'records'
    if not os.path.exists(folder):
        print('records 폴더가 없습니다.')
        return

    for filename in os.listdir(folder):
        if filename.endswith('.wav') and not filename.endswith('_converted.wav'):
            print(f'{filename} 처리 중...')
            save_text_to_csv(filename)

# 🔍 키워드 검색 기능
def search_keyword_in_csv(keyword):
    folder = 'records'
    found = False
    for filename in os.listdir(folder):
        if filename.endswith('.csv'):
            path = os.path.join(folder, filename)
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if keyword in row[1]:
                        print(f'[검색 결과] {filename} - {row[0]}: {row[1]}')
                        found = True
    if not found:
        print('키워드가 포함된 결과를 찾지 못했습니다.')

# ▶️ 메인 실행
if __name__ == '__main__':
    process_all_wav_files()
    keyword = input('검색할 키워드를 입력하세요: ')
    search_keyword_in_csv(keyword)
