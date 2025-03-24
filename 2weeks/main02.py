import pandas as pd
import pickle 

file = "Mars_Base_Inventory_List.csv"

# Mars_Base_Inventory_List.csv 의 내용을 읽어 들어서 출력한다
df = pd.read_csv(file)
print(df)

# Mars_Base_Inventory_List.csv 내용을 읽어서 Python의 리스트(List) 객체로 변환한다.  
Inventory_List = df.to_dict(orient="records")

# 배열 내용을 적제 화물 목록을 인화성이 높은 순으로 정렬한다.
sort_Inventory_List = sorted(Inventory_List, key=lambda x: float(x['Flammability']), reverse=True)

# 인화성 지수가 0.7 이상되는 목록을 뽑아서 별도로 출력한다
high_Inventory_List = [item for item in sort_Inventory_List if float(item['Flammability']) >= 0.7]
print(high_Inventory_List )

# 인화성 지수가 0.7 이상되는 목록을 CSV 포맷(Mars_Base_Inventory_danger.csv)으로 저장한다.
high_df = pd.DataFrame(high_Inventory_List)
high_df.to_csv("Mars_Base_Inventory_danger.csv", index=False)

# 인화성 순서로 정렬된 배열의 내용을 이진 파일형태로 저장한다. 파일이름은 Mars_Base_Inventory_List.bin
with open("Mars_Base_Inventory_List.bin", "wb") as bin_file:
    pickle.dump(sort_Inventory_List, bin_file)
print("Mars_Base_Inventory_List.bin")

# 정렬 후 저장장
with open("Mars_Base_Inventory_List.bin", "rb") as bin_file:
    loaded_inventory = pickle.load(bin_file)

# 저장된 Mars_Base_Inventory_List.bin 의 내용을 다시 읽어 들여서 화면에 내용을 출력한다.
print(" 이진 파일 출력")
for item in loaded_inventory:
    print(item)