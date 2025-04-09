import sys #런타임 설정이나 모듈 경로 관리 등에 사용
import os  #파일 경로를 다룸
import time
import json 
import threading #멀티스레드: 동시에 input 대기 + 무한 루프 실행
sys.path.append(os.path.abspath('../3weeks'))
# 경로 목록 sys.path에 '../3weeks'폴더를 강제로 추가
# os.path.abspath('../3weeks')는 상대경로 -> 절대경로로 바꿔줌
import platform
import psutil  #  메모리 정보(단 시스템 정보를 가져오는 부분은 별도의 라이브러리를 사용 할 수 있다. )


from dummy_sensor import DummySensor

# # 테스트용 인스턴스 생성
# ds = DummySensor()

# # 환경값 세팅
# ds.set_env()

# # 출력
# print("DummySensor에서 env_values: ")
# print(ds.get_env())

class MissionComputer:
    # DummySensor 인스턴스 생성
    ds = DummySensor()
    # 환경 데이터 저장 딕셔너리
    env_values = ds.env_values
    # 반복 종료 여부를(처음에는 계속 실행)
    stop_flag = False

    @staticmethod
    def wait_for_exit():
        input("종료하려면 아무 키나 누르세요\n")
        MissionComputer.stop_flag = True

    # get_sensor_data()메소드 추가
    def get_sensor_data(self):
        try:
            threading.Thread(target=MissionComputer.wait_for_exit, daemon=True).start()
            
            env_history = [] # 측정값 저장할 리스트
            start_time = time.time() #현재 시간
            
            while not MissionComputer.stop_flag:
                self.ds.set_env() # 센서 값 설정
                self.env_values = self.ds.get_env() # 값 받아오기

                # 딕셔너리 복사해서 저장
                env_history.append(self.env_values.copy())

                # Json 형태로 출력
                print(json.dumps(self.env_values, indent=2))

                # 5분(300초) 마다 평균 출력
                if time.time() - start_time >=300:
                    print("\n 5분 평균 환경값")
                    average = {}

                    keys = self.env_values.keys()
                    for key in keys:
                        values = [entry[key] for entry in env_history]
                        avg = round(sum(values) / len(values), 2)
                        average[key] = avg
                    print(json.dumps(average, indent=2))

                    # 초기화
                    env_history = []
                    start_time = time.time()

                # 5초마다 반복
                time.sleep(5)
                
            print("Sytem stoped….")
        except Exception as e:
            print("에러 발생:",e)

        
    @staticmethod
    def get_mission_computer_info():
        try:
            info = {
                "운영체제": platform.system(),
                "운영체제 버전": platform.version(),
                "CPU 종류": platform.processor(),
                "CPU 코어 수": os.cpu_count(),
                "메모리 크기(MB)": round(psutil.virtual_memory().total / (1024 ** 2), 2)
            }
            print("\n[미션 컴퓨터 시스템 정보]")
            print(json.dumps(info, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"[시스템 정보 수집 오류] {e}")
        with open("setting.txt", "a", encoding="utf-8") as f:
            f.write("\n[미션 컴퓨터 시스템 정보]\n")
            f.write(json.dumps(info, indent=2, ensure_ascii=False))
            f.write("\n")

    @staticmethod
    def get_mission_computer_load():
        try:
            load = {
                "CPU 실시간 사용량(%)": psutil.cpu_percent(interval=1),
                "메모리 사용량(%)": psutil.virtual_memory().percent
            }
            print("\n[미션 컴퓨터 실시간 부하]")
            print(json.dumps(load, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"[부하 정보 수집 오류] {e}")
        with open("setting.txt", "a", encoding="utf-8") as f:
            f.write("\n[미션 컴퓨터 실시간 부하]\n")
            f.write(json.dumps(load, indent=2, ensure_ascii=False))
            f.write("\n")



if __name__ == "__main__":
    # RunComputer 인스턴스화
    runComputer = MissionComputer()
    # 시스템 정보 출력
    runComputer.get_mission_computer_info()
    # 실시간 부하 출력
    runComputer.get_mission_computer_load()
    # 센서 출력 시작 지금은 필요없으니깐 주석처리
    #runComputer.get_sensor_data()


