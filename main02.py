import pandas as pd

file = "Mars_Base_Inventory_List.csv"

# Mars_Base_Inventory_List.csv 의 내용을 읽어 들어서 출력한다
df = pd.read_csv(file)
print(df)

# Mars_Base_Inventory_List.csv 내용을 읽어서 Python의 리스트(List) 객체로 변환한다.  
df_List = df.to_dict(orient="records")

# 배열 내용을 적제 화물 목록을 인화성이 높은 순으로 정렬한다.
sort_df_List = sorted(df_List, key=lambda x: float(x['Flammability']), reverse=True)

# 인화성 지수가 0.7 이상되는 목록을 뽑아서 별도로 출력한다
high_df_List = [item for item in sort_df_List if float(item['Flammability']) >= 0.7]
print(high_df_List )

# 인화성 지수가 0.7 이상되는 목록을 CSV 포맷(Mars_Base_Inventory_danger.csv)으로 저장한다.
high_df = pd.DataFrame(high_df_List)
high_df.to_csv("Mars_Base_Inventory_danger.csv")
print(high_df)