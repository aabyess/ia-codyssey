from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt #PyQt 라이브러리
import sys

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('iPhone Calculator')
        self.setGeometry(100, 100, 320, 600)  # 전체 창 크기를 좀 더 높여줌
        
        # 전체 배경 색상을 검정색으로 설정
        self.setStyleSheet("background-color: #000000;")  # 배경색을 검정색으로 설정
        
        # 디스플레이 화면 길이를 두 배로 길게 설정
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
        self.display.setFixedHeight(160)  # 디스플레이 화면 길이를 두 배로 설정

        # 버튼 배치 (아이폰 계산기 UI와 정확하게 일치)
        grid_layout = QGridLayout()
        buttons = [
            ('AC', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 2, 1), ('.', 4, 2), ('=', 4, 3),
        ]

        for button in buttons:
            text = button[0]
            row = button[1]
            col = button[2]
            colspan = button[3] if len(button) > 3 else 1
            rowspan = button[4] if len(button) > 4 else 1

            button_widget = QPushButton(text, self)
            button_widget.setFixedSize(80, 80)
            
            # 버튼을 원형으로 만들기 위한 설정
            if text == '0':
                # '0' 버튼은 두 칸을 차지하므로 타원형으로 만들어줍니다
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
            if text in ['AC', '±', '%', '÷', '×', '-', '+', '=', '±']:
                button_widget.setStyleSheet("""
                    background-color: #FF9500; 
                    color: white; 
                    font-size: 28px; 
                    border-radius: 40px;
                """)

            button_widget.clicked.connect(self.on_button_click)
            grid_layout.addWidget(button_widget, row, col, rowspan, colspan)

        # 레이아웃 설정
        vbox = QVBoxLayout()
        vbox.addWidget(self.display)
        vbox.addLayout(grid_layout)
        self.setLayout(vbox)

    def on_button_click(self):
        button_text = self.sender().text()
        current_text = self.display.text()

        if button_text == 'AC':
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
                # 계산 결과를 디스플레이에 출력
                result = eval(current_text.replace('÷', '/').replace('×', '*').replace('±', '-'))
                self.display.setText(str(result))
            except Exception:
                self.display.setText("Error")
        else:
            # 숫자나 연산자를 입력
            self.display.setText(current_text + button_text)

def main():
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
