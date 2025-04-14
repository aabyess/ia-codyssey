import tkinter as tk

# 버튼 클릭 이벤트 처리
def button_click(value):
    current_text = entry.get()
    entry.delete(0, tk.END)
    entry.insert(0, current_text + value)

# tkinter 창 생성
root = tk.Tk()
root.title("iPhone Style Calculator")
root.geometry("320x480")
root.resizable(False, False)

# 입력창
entry = tk.Entry(root, font=("Arial", 28), justify="right", bd=10, insertwidth=2, bg="white", fg="black")
entry.grid(row=0, column=0, columnspan=4, ipadx=8, ipady=15)

# 버튼 레이아웃
buttons = [
    ["C", "+/-", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "="]
]

# 버튼 색상
button_colors = {
    "C": "orange", "+/-": "lightgray", "%": "lightgray", "÷": "orange",
    "×": "orange", "-": "orange", "+": "orange", "=": "orange",
    "0": "white", ".": "white", "1": "white", "2": "white", "3": "white",
    "4": "white", "5": "white", "6": "white", "7": "white", "8": "white", "9": "white"
}

# 버튼 생성
for i, row in enumerate(buttons):
    for j, btn_text in enumerate(row):
        if btn_text == "0":
            btn = tk.Button(root, text=btn_text, font=("Arial", 18), bg=button_colors[btn_text], fg="black",
                            command=lambda value=btn_text: button_click(value))
            btn.grid(row=i+1, column=j, columnspan=2, sticky="nsew", ipadx=50, ipady=20)
        else:
            btn = tk.Button(root, text=btn_text, font=("Arial", 18), bg=button_colors[btn_text], fg="black",
                            command=lambda value=btn_text: button_click(value))
            btn.grid(row=i+1, column=j, sticky="nsew", ipadx=20, ipady=20)

# 그리드 크기 조정
for i in range(6):
    root.grid_rowconfigure(i, weight=1)
for j in range(4):
    root.grid_columnconfigure(j, weight=1)

# 메인 루프 실행
root.mainloop()