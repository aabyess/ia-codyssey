from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
import sys

# Calculator 클래스 정의 - QWidget 상속
class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()  # UI 초기화 메서드 호출

    def initUI(self):
        # 창 속성 설정
        self.setWindowTitle('iPhone Calculator')
        self.setGeometry(100, 100, 320, 600)
        self.setStyleSheet("background-color: #000000;")

        # 숫자 및 결과 표시 창 설정
        self.display = QLineEdit(self)
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self.display.setStyleSheet("""
            font-size: 32px;
            padding: 20px;
            color: white;
            background-color: #000000;
            border: none;
        """)
        self.display.setFixedHeight(160)

        # 버튼 레이아웃 설정
        grid_layout = QGridLayout()
        buttons = [
            ('AC', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 2, 1), ('.', 4, 2), ('=', 4, 3),
        ]

        # 버튼을 생성하고 UI에 추가
        for button in buttons:
            text, row, col = button[0], button[1], button[2]
            colspan = button[3] if len(button) > 3 else 1
            rowspan = button[4] if len(button) > 4 else 1

            button_widget = QPushButton(text, self)
            if text == '0':  # 0 버튼은 두 칸 차지
                button_widget.setMinimumSize(160, 80)
            else:
                button_widget.setFixedSize(80, 80)

            # 버튼 스타일 설정
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

            # 클릭 시 이벤트 연결
            button_widget.clicked.connect(self.on_button_click)
            grid_layout.addWidget(button_widget, row, col, rowspan, colspan)

        # 디스플레이와 버튼을 수직 배치
        vbox = QVBoxLayout()
        vbox.addWidget(self.display)
        vbox.addLayout(grid_layout)
        self.setLayout(vbox)

    # 버튼 클릭 시 호출되는 함수
    def on_button_click(self):
        button_text = self.sender().text()
        current_text = self.display.text()

        # 기능별 분기 처리
        if button_text == 'AC':
            self.reset()  # 초기화
        elif button_text == '±':
            self.negative_positive()  # 부호 전환
        elif button_text == '%':
            self.percent()  # 백분율 변환
        elif button_text == '=':
            self.equal()  # 수식 계산
        elif button_text == '.':
            # 중복 소수점 입력 방지
            if '.' not in current_text.split()[-1]:
                self.display.setText(current_text + '.')
        else:
            # 숫자 또는 연산자 입력
            self.display.setText(current_text + button_text)

        self.adjust_font_size()  # 결과 길이에 따른 폰트 조정

    # 디스플레이 초기화
    def reset(self):
        self.display.setText("")

    # 부호 변경
    def negative_positive(self):
        text = self.display.text()
        if text.startswith("-"):
            self.display.setText(text[1:])
        elif text:
            self.display.setText("-" + text)

    # 백분율 계산
    def percent(self):
        try:
            value = float(self.display.text())
            self.display.setText(str(value / 100))
        except:
            self.display.setText("Error")

    # 사칙연산 함수들
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("0으로 나눌 수 없습니다.")
        return a / b

    # 수식 평가 및 출력 (eval 사용 제거하고 사칙연산 메서드 사용)
    def equal(self):
        try:
            expr = self.display.text().replace('÷', '/').replace('×', '*')
            for op in ['+', '-', '*', '/']:
                if op in expr:
                    parts = expr.split(op)
                    if len(parts) == 2:
                        a, b = map(float, parts)
                        if op == '+':
                            result = self.add(a, b)
                        elif op == '-':
                            result = self.subtract(a, b)
                        elif op == '*':
                            result = self.multiply(a, b)
                        elif op == '/':
                            result = self.divide(a, b)
                        break
            if isinstance(result, float):
                result = round(result, 6)
            self.display.setText(str(result))
        except ZeroDivisionError:
            self.display.setText("Divide by 0 Error")
        except:
            self.display.setText("Error")

    # 디스플레이 길이에 따른 폰트 크기 자동 조절
    def adjust_font_size(self):
        length = len(self.display.text())
        if length <= 10:
            font_size = 32
        elif length <= 15:
            font_size = 24
        else:
            font_size = 18
        self.display.setStyleSheet(f"""
            font-size: {font_size}px;
            padding: 20px;
            color: white;
            background-color: #000000;
            border: none;
        """)

# 메인 함수: 애플리케이션 실행
def main():
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())

# 프로그램 진입점
if __name__ == '__main__':
    main()


#test

#0509