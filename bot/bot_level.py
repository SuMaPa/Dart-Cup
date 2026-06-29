import sys
from PyQt6.QtWidgets import (
    QApplication,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QStyledItemDelegate,
    QStyle,
)
from PyQt6.QtCore import Qt


class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Jetzt kennt Python QStyle dank des Imports oben
        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)


def load_data(file_path):
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "Level" in line:
                parts = line.split(",", 1)
                data.append([parts[0].strip(), parts[1].strip().strip('"')])
    return data


app = QApplication(sys.argv)

app.setStyleSheet("""
    QWidget { background-color: #1e1e1e; color: #ffffff; }
    QTableWidget {
        background-color: #1e1e1e;
        alternate-background-color: #2b2b2b;
        selection-background-color: transparent;
        selection-color: white;
    }
    QTableWidget::item { border: none; }
    QPushButton { background-color: #333; border: 1px solid #555; padding: 5px; }
    QPushButton:hover { background-color: #444; }
""")

main_win = QWidget()
layout = QVBoxLayout(main_win)

table = QTableWidget(10, 2)
# Delegate setzen
table.setItemDelegate(NoFocusDelegate())
table.setHorizontalHeaderLabels(["Level", "Beschreibung"])

for row, (lvl, desc) in enumerate(load_data("bot_level.txt")):
    table.setItem(row, 0, QTableWidgetItem(lvl))
    table.setItem(row, 1, QTableWidgetItem(desc))

table.horizontalHeader().setStretchLastSection(True)
table.setMinimumSize(800, 400)

btn_close = QPushButton("Schließen")
btn_close.clicked.connect(main_win.close)

layout.addWidget(table)
layout.addWidget(btn_close)

main_win.show()
sys.exit(app.exec())
