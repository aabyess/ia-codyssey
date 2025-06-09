import csv
import mysql.connector

class MySQLHelper:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def execute(self, query, params=None):
        self.cursor.execute(query, params)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

def create_table(db):
    create_query = (
        'CREATE TABLE IF NOT EXISTS mars_weather ('
        'weather_id INT AUTO_INCREMENT PRIMARY KEY, '
        'mars_date DATETIME NOT NULL, '
        'temp INT, '
        'storm INT)'
    )
    db.execute(create_query)

def insert_data_from_csv(db, csv_file):
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            insert_query = (
                'INSERT INTO mars_weather (mars_date, temp, storm) '
                'VALUES (%s, %s, %s)'
            )
            mars_date = row['mars_date']
            temp = int(float(row['temp']))
            storm = int(row['stom'])  # "storm" is misspelled as "stom" in CSV
            db.execute(insert_query, (mars_date, temp, storm))

def main():
    db = MySQLHelper(
        host='localhost',
        user='root',
        password='your_password',
        database='your_database'
    )

    create_table(db)
    insert_data_from_csv(db, 'mars_weathers_data.CSV')
    db.close()

if __name__ == '__main__':
    main()
