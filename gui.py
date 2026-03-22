import sys, serial
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QComboBox, QLineEdit, QVBoxLayout, QHBoxLayout,
    QProgressBar
)
from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal
import controller as arduino

values = {"" : ""}

class ArduinoWorker(QObject):
    finished = pyqtSignal(bool)

    def run(self):
        found = arduino.get_arduino()
        self.finished.emit(found)


class Controlino(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Controlino")
        self.resize(600, 250)

        self.layout = QVBoxLayout()

        self.status_label = QLabel("Searching for Arduino...")
        self.layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.layout.addWidget(self.progress)

        self.setLayout(self.layout)

        self.start_search()

    def start_search(self):

        self.thread = QThread()
        self.worker = ArduinoWorker()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.search_finished)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def manual_connect(self, port):
        try:
            arduino.arduino = serial.Serial(port, 115200, timeout=2)
        except Exception:
            self.error.setText(f"Can't connect to {port}")
            return False
        self.error.setText(f"Connected on {port}")
        QTimer.singleShot(1500, self.load_main_screen)

    def search_finished(self, found):

        if found:
            self.status_label.setText(f"Arduino found on {arduino.port_name}")
            self.progress.hide()
            QTimer.singleShot(1500, self.load_main_screen)
        else:
            row = QHBoxLayout()
            self.status_label.setText("Arduino not found")

            port = QLineEdit()
            port.setPlaceholderText("Port")

            send_btn = QPushButton("Connect")
            send_btn.clicked.connect(lambda: self.manual_connect(port.text()))

            self.error = QLabel("")

            row.addWidget(QLabel("Port: "))
            row.addWidget(port)
            row.addWidget(send_btn)
            self.layout.addLayout(row)
            self.layout.addWidget(self.error)
            self.layout.addStretch()

            self.progress.hide()

    def clear_layout(self):

        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()
            else:
                sublayout = item.layout()
                if sublayout:
                    while sublayout.count():
                        subitem = sublayout.takeAt(0)
                        if subitem.widget():
                            subitem.widget().deleteLater()

    def load_main_screen(self):

        self.clear_layout()

        # row1
        row1 = QHBoxLayout()

        self.ad_mode = QComboBox()
        self.ad_mode.addItems(["Digital", "Analog"])

        self.pin_mode = QComboBox()
        self.pin_mode.addItems(["Write", "Read"])
        self.pin_mode.currentTextChanged.connect(self.mode_changed)

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Pin")

        row1.addWidget(self.ad_mode)
        row1.addWidget(self.pin_mode)
        row1.addWidget(QLabel("Pin"))
        row1.addWidget(self.pin_input)

        self.layout.addLayout(row1)

        # row2
        self.row2 = QHBoxLayout()

        self.row2.addWidget(QLabel("Value: "))

        self.value_widget = QLineEdit()
        self.row2.insertWidget(1, self.value_widget)

        self.saved_value = QComboBox()
        self.saved_value.addItems(list(values.keys()))
        self.saved_value.currentTextChanged.connect(self.value_changed)
        self.row2.insertWidget(2, self.saved_value)


        self.row2.addStretch()

        self.layout.addLayout(self.row2)

        # row3
        row3 = QHBoxLayout()

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_instruction)

        row3.addWidget(send_btn)

        self.layout.addLayout(row3)

        self.layout.addStretch()

    def mode_changed(self):

        mode = self.pin_mode.currentText()

        self.row2.removeWidget(self.value_widget)
        self.value_widget.deleteLater()

        if mode == "Write":
            self.row2.removeWidget(self.save_text_widget)
            self.row2.removeWidget(self.name_widget)
            self.row2.removeWidget(self.save_btn)
            self.save_text_widget.deleteLater()
            self.name_widget.deleteLater()
            self.save_btn.deleteLater()

            self.value_widget = QLineEdit()
            self.row2.insertWidget(1, self.value_widget)
            self.saved_value = QComboBox()
            self.saved_value.addItems(list(values.keys()))
            self.saved_value.currentTextChanged.connect(self.value_changed)
            self.row2.insertWidget(2, self.saved_value)
        else:
            self.row2.removeWidget(self.saved_value)
            self.saved_value.deleteLater()

            self.value_widget = QLabel("-")
            self.save_text_widget = QLabel("save as")
            self.name_widget = QLineEdit()
            self.save_btn = QPushButton("Save")
            self.save_btn.clicked.connect(self.save_value)
            self.row2.insertWidget(1, self.value_widget)
            self.row2.insertWidget(3, self.save_text_widget)
            self.row2.insertWidget(4, self.name_widget)
            self.row2.insertWidget(5, self.save_btn)

    def save_value(self):
        values[self.name_widget.text()] = self.value_widget.text()

    def value_changed(self):
        self.value_widget.setText(values[self.saved_value.currentText()])

    def send_instruction(self):

        pin = self.pin_input.text()
        pin_mode = self.pin_mode.currentText()
        ad_mode = self.ad_mode.currentText()

        value = ""

        if isinstance(self.value_widget, QLineEdit):
            value = self.value_widget.text()

        response = arduino.send_instruction(
            pin,
            pin_mode,
            ad_mode,
            value
        )

        if response[0] == "VALUE":
            self.value_widget.setText(response[1])


def run():
    app = QApplication(sys.argv)
    window = Controlino()
    window.show()
    sys.exit(app.exec())