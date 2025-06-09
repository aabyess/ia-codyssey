import csv
import mysql.connector

# MySQL 연결과 쿼리 실행을 도와주는 헬퍼 클래스
class MySQLHelper:
    def __init__(self, host, user, password, database):
        # DB 연결 수행
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    # 쿼리 실행 (INSERT, CREATE 등)
    def execute(self, query, params=None):
        self.cursor.execute(query, params)
        self.connection.commit()

    # 연결 종료
    def close(self):
        self.cursor.close()
        self.connection.close()

# mars_weather 테이블 생성 함수
def create_table(db):
    create_query = (
        'CREATE TABLE IF NOT EXISTS mars_weather ('
        'weather_id INT AUTO_INCREMENT PRIMARY KEY, '
        'mars_date DATETIME NOT NULL, '
        'temp INT, '
        'storm INT)'
    )
    db.execute(create_query)

# CSV 파일을 읽고 테이블에 삽입하는 함수
def insert_data_from_csv(db, csv_file):
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            insert_query = (
                'INSERT INTO mars_weather (mars_date, temp, storm) '
                'VALUES (%s, %s, %s)'
            )
            mars_date = row['mars_date']  # 날짜 그대로 사용
            temp = int(float(row['temp']))  # 소수 → 정수 변환
            storm = int(row['stom'])  # CSV 오타(stom)를 storm으로 처리
            db.execute(insert_query, (mars_date, temp, storm))

# 전체 실행 흐름을 제어하는 메인 함수
def main():
    db = MySQLHelper(
        host='localhost',
        user='root',
        password='3535',  # 설치 시 지정한 비밀번호
        database='mars_db'
    )

    create_table(db)  # 테이블 생성
    insert_data_from_csv(db, 'mars_weathers_data.CSV')  # 데이터 삽입
    db.close()  # DB 연결 종료

# 실행
if __name__ == '__main__':
    main()