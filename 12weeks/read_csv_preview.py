import csv

def read_csv_preview(filename):
    with open(filename, newline='') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            print(row)
            if i == 4:  # 5개만 미리보기
                break

if __name__ == '__main__':
    read_csv_preview('mars_weathers_data.CSV')
