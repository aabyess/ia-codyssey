import random

# 더미 센서에 해당하는 클래스를 생성한다. 클래스의 이름은 DummySensor로 정의한다. 
class DummySensor:
    # DummySensor의 멤버로 env_values라는 사전 객체를 추가한다. 사전 객체에는 다음과 같은 항목들이 추가 되어 있어야 한다. 
    def __init__(self):
       self.env_values = {
            "mars_base_internal_temperature": 0.0,
            "mars_base_external_temperature": 0.0,
            "mars_base_internal_humidity": 0.0,
            "mars_base_external_illuminance": 0.0,
            "mars_base_internal_co2": 0.0,
            "mars_base_internal_oxygen": 0.0
        }
    # DummySensor는 테스트를 위한 객체이므로 데이터를 램덤으로 생성한다. 
    # DummySensor 클래스에 set_env() 메소드를 추가한다. set_env() 메소드는 random으로 주어진 범위 안의 값을 생성해서
    # env_values 항목에 채워주는 역할을 한다. 각 항목의 값의 범위는 다음과 같다. 
    def set_env(self):
        self.env_values["mars_base_internal_temperature"] = round(random.uniform(18, 30), 2)
        self.env_values["mars_base_external_temperature"] = round(random.uniform(0, 21), 2)
        self.env_values["mars_base_internal_humidity"] = round(random.uniform(50, 60), 2)
        self.env_values["mars_base_external_illuminance"] = round(random.uniform(500, 715), 2)
        self.env_values["mars_base_internal_co2"] = round(random.uniform(0.02, 0.1), 4)
        self.env_values["mars_base_internal_oxygen"] = round(random.uniform(4.0, 7.0), 2)
    # DummySensor 클래스는 get_env() 메소드를 추가하는데 get_env() 메소드는 env_values를 return 한다
    def get_env(self):
        return self.env_values
    
# DummySensor 클래스를 ds라는 이름으로 인스턴스(Instance)로 만든다. 
# 인스턴스화 한 DummySensor 클래스에서 set_env()와 get_env()를 차례로 호출해서 값을 확인한다. 
if __name__ == "__main__":
    ds = DummySensor()
    ds.set_env() #랜덤 센서값 측정 요청 
    values = ds.get_env()  #센서 값이 저장된 env_values 딕셔너리를 가져와서, values라는 변수에 저장
    print("DummySensor 측정값:")
    for key, value in values.items():
        print(f"{key}: {value}")