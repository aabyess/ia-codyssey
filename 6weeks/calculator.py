from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt # Qt는 정렬 등 다양한 상수를 제공
import sys # 프로그램 종료 등을 위해 사용

# QWidget을 상속한 Calculator 클래스
class Calculator(QWidget):
    def __init__(self): # __init__ 생성자에서 initUI() 메서드를 호출해 UI 초기화
        super().__init__()  # 부모 클래스(QWidget)의 생성자 호출
        self.initUI()  # 이 클래스의 UI를 구성하는 메서드 호출

    def initUI(self): # 계산기 UI를 설정하는 메서드
        self.setWindowTitle('iPhone Calculator')
        self.setGeometry(100, 100, 320, 600)  # 창 제목과 위치/크기
        self.setStyleSheet("background-color: #000000;")  # 배경색을 검정색으로 설정
        
        # 디스플레이 스타일 설정
        self.display = QLineEdit(self)
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignBottom | Qt.AlignRight)  # 숫자가 디스플레이 바닥에 붙도록 설정
        self.display.setStyleSheet("""
            font-size: 32px;
            padding: 20px;
            color: white;  /* 글자색을 흰색으로 설정 */
            background-color: #000000;  /* 배경을 검정색으로 변경 */
            border: none;
        """) 
        self.display.setFixedHeight(160)  # 디스플레이 화면 길이 설정

        # 버튼 배치 (아이폰 계산기 UI)
        grid_layout = QGridLayout()
        buttons = [ # 각 튜플: (버튼 이름, 행, 열)
            ('AC', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 2, 1), ('.', 4, 2), ('=', 4, 3),
        ]
        # 버튼 정의에서 텍스트와 위치, 병합 크기를 파악
        for button in buttons:
            text = button[0]
            row = button[1]
            col = button[2]
            colspan = button[3] if len(button) > 3 else 1
            rowspan = button[4] if len(button) > 4 else 1

            # 버튼 위젯을 만들고 고정 크기를 설정
            button_widget = QPushButton(text, self)
            button_widget.setFixedSize(80, 80)
            
            # 버튼을 원형으로 만들기 위한 설정
            if text == '0':
                button_widget.setMinimumSize(160, 80)  # 두 칸이므로 160
                # '0' 버튼은 두 칸을 차지하므로 타원형으로 만들어줌
                button_widget.setStyleSheet("""
                    background-color: #333333; 
                    color: white; 
                    font-size: 28px; 
                    border-radius: 40px;
                """)
            else:
                # 나머지 버튼들은 원형으로 설정
                button_widget.setStyleSheet("""
                    background-color: #333333; 
                    color: white; 
                    font-size: 28px; 
                    border-radius: 40px;
                """)

            # 연산자 버튼의 스타일
            if text in ['AC', '±', '%']:
                button_widget.setStyleSheet("""
                    background-color: #A5A5A5;
                    color: black;
                    font-size: 28px;
                    border-radius: 40px;
                """)
            elif text in ['÷', '×', '-', '+', '=']:
                button_widget.setStyleSheet("""
                    background-color: #FF9500;
                    color: white;
                    font-size: 28px;
                    border-radius: 40px;
                """)
            else:
                button_widget.setStyleSheet("""
                    background-color: #333333;
                    color: white;
                    font-size: 28px;
                    border-radius: 40px;
                """)


            # 버튼 클릭 시 이벤트 연결, 레이아웃에 버튼 추가
            button_widget.clicked.connect(self.on_button_click)
            grid_layout.addWidget(button_widget, row, col, rowspan, colspan)

        # 세로 박스 레이아웃을 사용해 디스플레이 + 버튼 격자 구성.
        vbox = QVBoxLayout()
        vbox.addWidget(self.display)
        vbox.addLayout(grid_layout)
        self.setLayout(vbox)

    #버튼 클릭 이벤트 처리
    def on_button_click(self):
        # 클릭된 버튼의 텍스트와 현재 디스플레이 텍스트 가져오기.
        button_text = self.sender().text()
        current_text = self.display.text()

        if button_text == 'AC':
            # AC 누르면 초기화
            self.display.clear()
        elif button_text == '±':
            # ± 버튼을 눌렀을 때, 부호 변경 처리
            if current_text:
                if current_text[0] == '-':
                    self.display.setText(current_text[1:])
                else:
                    self.display.setText('-' + current_text)
        elif button_text == '=':
            try:
                # = 버튼 누르면 수식 계산 (÷ → /, × → *, ± → - 로 변환 후 eval)
                result = eval(current_text.replace('÷', '/').replace('×', '*').replace('±', '-'))
                self.display.setText(str(result))
            except Exception:
                self.display.setText("Error")
        else:
            # 숫자나 연산자 버튼이면 그냥 이어 붙임
            self.display.setText(current_text + button_text)

# PyQt 앱 생성 및 실행 루프 시작
def main():
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
