from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
import sys

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('iPhone Calculator')
        self.setGeometry(100, 100, 320, 600)
        self.setStyleSheet("background-color: #000000;")

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

        grid_layout = QGridLayout()
        buttons = [
            ('AC', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 2, 1), ('.', 4, 2), ('=', 4, 3),
        ]

        for button in buttons:
            text, row, col = button[0], button[1], button[2]
            colspan = button[3] if len(button) > 3 else 1
            rowspan = button[4] if len(button) > 4 else 1

            button_widget = QPushButton(text, self)
            if text == '0':
                button_widget.setMinimumSize(160, 80)
            else:
                button_widget.setFixedSize(80, 80)

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

            button_widget.clicked.connect(self.on_button_click)
            grid_layout.addWidget(button_widget, row, col, rowspan, colspan)

        vbox = QVBoxLayout()
        vbox.addWidget(self.display)
        vbox.addLayout(grid_layout)
        self.setLayout(vbox)

    def on_button_click(self):
        button_text = self.sender().text()
        current_text = self.display.text()

        if button_text == 'AC':
            self.reset()
        elif button_text == '±':
            self.negative_positive()
        elif button_text == '%':
            self.percent()
        elif button_text == '=':
            self.equal()
        elif button_text == '.':
            if '.' not in current_text.split()[-1]:
                self.display.setText(current_text + '.')
        else:
            self.display.setText(current_text + button_text)
        self.adjust_font_size()

    def reset(self):
        self.display.setText("")

    def negative_positive(self):
        text = self.display.text()
        if text.startswith("-"):
            self.display.setText(text[1:])
        elif text:
            self.display.setText("-" + text)

    def percent(self):
        try:
            value = float(self.display.text())
            self.display.setText(str(value / 100))
        except:
            self.display.setText("Error")

    def equal(self):
        try:
            expr = self.display.text().replace('÷', '/').replace('×', '*')
            result = eval(expr)
            if isinstance(result, float):
                result = round(result, 6)
            self.display.setText(str(result))
        except ZeroDivisionError:
            self.display.setText("Divide by 0 Error")
        except:
            self.display.setText("Error")

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

def main():
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
