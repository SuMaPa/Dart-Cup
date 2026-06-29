# ui/spiel/killer.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QFont


def get_stats_widget(match_data):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    w = QWidget()
    layout = QVBoxLayout(w)
    layout.addWidget(QLabel("<b>Auswertung: Killer</b>"))
    layout.addWidget(
        QLabel(f"Letzter Überlebender: {match_data.get('gewinner', 'N/A')}")
    )
    layout.addStretch()
    scroll.setWidget(w)
    return scroll


def get_live_widget(game):
    table = QTableWidget()
    table.setRowCount(len(game.players))
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels(["Spieler", "Nummer", "Leben"])
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    update_live_widget(game, table)
    return table


def update_live_widget(game, table):
    current_p = game.current_player_idx
    killer_numbers = getattr(game, "killer_numbers", [0] * len(game.players))
    killer_status = getattr(game, "killer_status", [False] * len(game.players))
    finished_players = getattr(game, "finished_players", [])

    for row_idx, player_name in enumerate(game.players):
        # KORREKTUR: Nur als eliminiert markieren, wenn der Spieler in finished_players ist UND 0 Leben hat
        is_eliminated = (row_idx in finished_players) and (game.scores[row_idx] <= 0)

        # NEU: Der Gewinner steht am Ende in finished_players, hat aber noch verbleibende Leben!
        is_winner = (row_idx in finished_players) and (game.scores[row_idx] > 0)

        # 1. Spalte: Spielername
        name_item = QTableWidgetItem(player_name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if is_eliminated:
            font = name_item.font()
            font.setStrikeOut(True)  # Verlierer durchstreichen
            name_item.setFont(font)
            name_item.setForeground(QBrush(QColor("#ff4c4c")))  # Rot markieren
        elif is_winner:
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            name_item.setForeground(
                QBrush(QColor("gold"))
            )  # Gewinner in Gold erstrahlen lassen!
            name_item.setBackground(QBrush(QColor("#2a2e32")))
        elif row_idx == current_p:
            name_item.setForeground(QBrush(QColor("gold")))
            name_item.setBackground(QBrush(QColor("#2a2e32")))
        else:
            name_item.setBackground(QBrush(QColor("transparent")))

        table.setItem(row_idx, 0, name_item)

        # 2. Spalte: Nummer
        num_val = killer_numbers[row_idx]
        if num_val == 0:
            num_str = "Wählen..."
        else:
            # Ein Stern symbolisiert den erlangten Killer-Status
            num_str = f"★ {num_val}" if killer_status[row_idx] else str(num_val)

        num_item = QTableWidgetItem(num_str)
        num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if is_eliminated:
            font = num_item.font()
            font.setStrikeOut(True)  # Nummer durchstreichen
            num_item.setFont(font)
            num_item.setForeground(QBrush(QColor("#ff4c4c")))
        elif is_winner:
            num_item.setForeground(QBrush(QColor("gold")))
            num_item.setBackground(QBrush(QColor("#2a2e32")))
            font = num_item.font()
            font.setBold(True)
            num_item.setFont(font)
        elif row_idx == current_p:
            num_item.setBackground(QBrush(QColor("#2a2e32")))
            num_item.setForeground(QBrush(QColor("#3daee9")))
        else:
            if killer_status[row_idx]:
                num_item.setForeground(
                    QBrush(QColor("#fdbc4b"))
                )  # Goldgelb für aktive Killer
            num_item.setBackground(QBrush(QColor("transparent")))

        table.setItem(row_idx, 1, num_item)

        # 3. Spalte: Leben (als fette Kreuze "X X X" oder als "SIEG!")
        lives_count = game.scores[row_idx]

        if is_winner:
            lives_str = "SIEG!"
        elif is_eliminated or lives_count <= 0:
            lives_str = ""
        else:
            lives_str = " ".join(["X"] * lives_count)

        lives_item = QTableWidgetItem(lives_str)
        lives_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont()
        font.setBold(True)
        font.setPointSize(13)
        lives_item.setFont(font)

        if is_winner:
            lives_item.setForeground(
                QBrush(QColor("gold"))
            )  # Goldene Schrift für den Sieg
            lives_item.setBackground(QBrush(QColor("#2a2e32")))
        else:
            lives_item.setForeground(QBrush(QColor("#27ae60")))  # Grün für aktive Leben

        if row_idx == current_p and not is_winner:
            lives_item.setBackground(QBrush(QColor("#2a2e32")))
        elif not is_winner:
            lives_item.setBackground(QBrush(QColor("transparent")))

        table.setItem(row_idx, 2, lives_item)
