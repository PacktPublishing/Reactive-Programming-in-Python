import sys
from PyQt5.QtWidgets import QApplication, QWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.resize(250, 150)
    window.move(350, 200)
    window.setWindowTitle('Hello World!')
    window.show()
    sys.exit(app.exec_())
