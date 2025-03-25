import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QGridLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class SensorReadoutWidget(QWidget):
    def __init__(self, sensor_name, scale_readout, timer_readout):
        super().__init__()

        self.initUI(sensor_name, scale_readout, timer_readout)

    def initUI(self, sensor_name, scale_readout, timer_readout):
        vbox = QVBoxLayout()

        self.sensor_label = QLabel(sensor_name, self)
        self.sensor_label.setFont(QFont('Arial', 20))
        self.sensor_label.setStyleSheet('color: #f4f4f4;')
        self.sensor_label.setAlignment(Qt.AlignCenter)

        self.scale_label = QLabel(scale_readout, self)
        self.scale_label.setFont(QFont('Arial', 40))
        self.scale_label.setStyleSheet('color: #f4f4f4; font-weight: bold;')
        self.scale_label.setAlignment(Qt.AlignCenter)

        self.timer_label = QLabel(timer_readout, self)
        self.timer_label.setFont(QFont('Arial', 20))
        self.timer_label.setStyleSheet('color: #f4f4f4;')
        self.timer_label.setAlignment(Qt.AlignCenter)

        vbox.addWidget(self.sensor_label)
        vbox.addWidget(self.scale_label)
        vbox.addWidget(self.timer_label)

        self.setLayout(vbox)

    def update_labels(self, scale_readout, timer_readout):
        self.scale_label.setText(scale_readout)
        self.timer_label.setText(timer_readout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Filling Machine")
        self.setGeometry(100, 100, 1200, 600)
        self.setStyleSheet('background-color: #292929;')
        #self.showFullScreen()

        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        grid_layout = QGridLayout()

        self.sensor1_widget = SensorReadoutWidget("Sensor 1", "Scale Readout 1", "Timer Readout 1")
        self.sensor2_widget = SensorReadoutWidget("Sensor 2", "Scale Readout 2", "Timer Readout 2")
        self.sensor3_widget = SensorReadoutWidget("Sensor 3", "Scale Readout 3", "Timer Readout 3")
        self.sensor4_widget = SensorReadoutWidget("Sensor 4", "Scale Readout 4", "Timer Readout 4")

        grid_layout.addWidget(self.sensor1_widget, 0, 0)
        grid_layout.addWidget(self.sensor2_widget, 0, 1)
        grid_layout.addWidget(self.sensor3_widget, 1, 0)
        grid_layout.addWidget(self.sensor4_widget, 1, 1)

        central_widget.setLayout(grid_layout)

    def update_sensor_labels(self, sensor_index, scale_readout, timer_readout):
        if sensor_index == 1:
            self.sensor1_widget.update_labels(scale_readout, timer_readout)
        elif sensor_index == 2:
            self.sensor2_widget.update_labels(scale_readout, timer_readout)
        elif sensor_index == 3:
            self.sensor3_widget.update_labels(scale_readout, timer_readout)
        elif sensor_index == 4:
            self.sensor4_widget.update_labels(scale_readout, timer_readout)

    def show_message(self, message, weight, time_remaining):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"{message}\nWeight: {weight:.1f} oz\nTime Remaining: {time_remaining:.1f} s")
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_clear_scale_warning(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("CLEAR SCALE")
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()