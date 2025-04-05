import sys #런타임 설정이나 모듈 경로 관리 등에 사용
import os  #파일 경로를 다룸
import time
import json 
import threading #멀티스레드: 동시에 input 대기 + 무한 루프 실행
sys.path.append(os.path.abspath('../3weeks'))
# 경로 목록 sys.path에 '../3weeks'폴더를 강제로 추가
# os.path.abspath('../3weeks')는 상대경로 -> 절대경로로 바꿔줌

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

# RunComputer 인스턴스화
RunComputer = MissionComputer()

RunComputer.get_sensor_data()


