import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QFont


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Filling Machine")
        self.setGeometry(100, 100, 800, 600)
        #self.showFullScreen()

        label = QLabel("Hello World!", self)
        label.setFont(QFont('Arial', 20))
        label.setGeometry(0, 0, 500, 100)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()