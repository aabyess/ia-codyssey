def parse_flammability(value):
    try:
        return float(value)
    except ValueError:
        return -1  # 유효하지 않은 값은 최소값으로 처리

def read_inventory_csv(file_path):
    inventory = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            headers = lines[0].strip().split(',')
            for line in lines[1:]:
                values = line.strip().split(',')
                item = dict(zip(headers, values))
                inventory.append(item)
    except Exception as e:
        print(f"[오류] 파일 읽기 실패: {e}")
    return inventory

def save_to_csv(file_path, data):
    try:
        with open(file_path, 'w') as file:
            if data:
                headers = data[0].keys()
                file.write(','.join(headers) + '\n')
                for item in data:
                    file.write(','.join(item.values()) + '\n')
        print(f"[성공] 파일 저장 완료: {file_path}")
    except Exception as e:
        print(f"[오류] 파일 저장 실패: {e}")

# 실행 경로 설정
input_file = 'C:\\Python\\2weeks\\Mars_Base_Inventory_List.csv'
output_file = 'C:\\Python\\2weeks\\Mars_Base_Inventory_danger.csv'

# 1. CSV 읽기
inventory = read_inventory_csv(input_file)

# 2. 인화성 기준 정렬 (내림차순)
sorted_inventory = sorted(inventory, key=lambda x: parse_flammability(x['Flammability']), reverse=True)

# 3. 인화성 ≥ 0.7인 항목 필터링
dangerous_items = [item for item in sorted_inventory if parse_flammability(item['Flammability']) >= 0.7]

# 4. 위험 목록 출력
print("인화성 높은 적재 목록 (Flammability ≥ 0.7):")
for item in dangerous_items:
    print(f"- {item['Substance']} (Flammability: {item['Flammability']})")

# 5. CSV로 저장
save_to_csv(output_file, dangerous_items)
