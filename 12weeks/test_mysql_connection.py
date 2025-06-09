import mysql.connector

def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='3535',
            database='mars_db'
        )
        if connection.is_connected():
            print(' MySQL 연결 성공!')
            connection.close()
    except mysql.connector.Error as e:
        print(f' 연결 실패: {e}')

if __name__ == '__main__':
    connect_to_mysql()
