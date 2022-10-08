import requests
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from datetime import datetime
import os

current_datetime = datetime.now()
version = requests.get('https://pastebin.com/raw/YDyNZ5Py').text
year = current_datetime.year

class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok
        self.buttonbox = QDialogButtonBox(QBtn)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("SolenoxBrowser")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('data/images', 'logo.png')))
        layout.addWidget(logo)

        layout.addWidget(QLabel(f"Version {version}"))
        layout.addWidget(QLabel(f"Copyright {year} SolenoxProject"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonbox)

        self.setLayout(layout)