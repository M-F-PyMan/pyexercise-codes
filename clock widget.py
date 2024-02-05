import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSizePolicy, QVBoxLayout
from PyQt5.QtGui import QFont, QPalette, QCursor
from PyQt5.QtCore import QTimer, QTime, Qt, QPoint

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clock Widget")
        self.resize(200, 100)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.label = QLabel()
        self.label.setFont(QFont("Arial", 32))
        self.label.setPalette(QPalette(Qt.white))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setStyleSheet("color: white; font-family: Biting My Nails; font-size: 32px;")


        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.label)
        mainLayout.addStretch(1) # this will add a vertical spacer to the layout
        self.setLayout(mainLayout)

        # new code to remove the background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
# this will make the widget always on top

        # new code to move the widget with the mouse
        self.oldPos = self.pos()
        self.setCursor(QCursor(Qt.OpenHandCursor))

    def update_time(self):
        current_time = QTime.currentTime()
        time_string = current_time.toString("HH:mm:ss")
        self.label.setText(time_string)

    # new code to move the widget with the mouse
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

app = QApplication(sys.argv)
clock = ClockWidget()
clock.show()
sys.exit(app.exec())
