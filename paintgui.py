import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, scale_readout, timer_readout):
        super().__init__()

        self.setWindowTitle("Filling Machine")
        self.setGeometry(100, 100, 1200, 300)
        self.setStyleSheet('background-color: #292929;')
        #self.showFullScreen()

        self.initUI(scale_readout, timer_readout)

    def initUI(self, scale_readout, timer_readout):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.label1 = QLabel(scale_readout, self)
        self.label1.setFont(QFont('Arial', 40))
        self.label1.setGeometry(0, 0, 700, 200)
        self.label1.setStyleSheet('color: #f4f4f4;'
                            'font-weight: bold;')
        self.label1.setAlignment(Qt.AlignCenter)

        self.label2 = QLabel(timer_readout, self)
        self.label2.setFont(QFont('Arial', 20))
        self.label2.setGeometry(0, 100, 500, 100)
        self.label2.setStyleSheet('color: #f4f4f4;')  
        self.label2.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label1)
        vbox.addWidget(self.label2)
        central_widget.setLayout(vbox)

    def update_labels(self, scale_readout, timer_readout):
        self.label1.setText(scale_readout)
        self.label2.setText(timer_readout)

def main():
    app = QApplication(sys.argv)
    scale_readout = "Scale Readout"  # Replace with actual value from paintpour.py
    timer_readout = "Timer Readout"  # Replace with actual value from paintpour.py
    window = MainWindow(scale_readout, timer_readout)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()