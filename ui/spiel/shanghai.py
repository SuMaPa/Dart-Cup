# ui/spiel/shanghai.py
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
    layout.addWidget(QLabel("<b>Auswertung: Shanghai</b>"))
    layout.addWidget(QLabel(f"Gewinner: {match_data.get('gewinner', 'N/A')}"))
    layout.addStretch()
    scroll.setWidget(w)
    return scroll


def get_live_widget(game):
    table = QTableWidget()
    table.setRowCount(len(game.players))
    table.setColumnCount(5)  # Spieler | Dart 1 | Dart 2 | Dart 3 | Score
    table.setHorizontalHeaderLabels(["Spieler", "Dart 1", "Dart 2", "Dart 3", "Score"])
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    update_live_widget(game, table)
    return table


def update_live_widget(game, table):
    current_p = game.current_player_idx
    finished_players = getattr(game, "finished_players", [])
    game_over = len(finished_players) >= len(game.players)

    for row_idx, player_name in enumerate(game.players):
        # Erkennt Sofortsieg (durch "SHANGHAI!" oder erfolgreiches Leg-Finish)
        is_winner = (row_idx in finished_players) and (
            game.scores[row_idx] in ["SHANGHAI!", 0]
        )
        is_finished = row_idx in finished_players

        # 1. Spalte: Spielername
        name_item = QTableWidgetItem(player_name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if is_winner:
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            name_item.setForeground(QBrush(QColor("gold")))
            name_item.setBackground(QBrush(QColor("#2a2e32")))
        elif row_idx == current_p:
            name_item.setForeground(QBrush(QColor("gold")))
            name_item.setBackground(QBrush(QColor("#2a2e32")))
        else:
            name_item.setBackground(QBrush(QColor("transparent")))
            name_item.setForeground(QBrush(QColor("white")))

        table.setItem(row_idx, 0, name_item)

        # 2., 3. und 4. Spalte: Darts (Dart 1, Dart 2, Dart 3)
        thrown = game.last_darts[row_idx] if row_idx < len(game.last_darts) else []
        for d_idx in range(3):
            val_str = thrown[d_idx] if d_idx < len(thrown) else ""
            item = QTableWidgetItem(val_str)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if row_idx == current_p:
                item.setBackground(QBrush(QColor("#2a2e32")))
                item.setForeground(QBrush(QColor("#3daee9")))
            else:
                item.setBackground(QBrush(QColor("transparent")))
                item.setForeground(QBrush(QColor("white")))

            table.setItem(row_idx, d_idx + 1, item)

        # 5. Spalte: Score (Gesamtpunkte oder Restpunkte)
        score_val = game.scores[row_idx]

        if is_winner:
            score_str = "SHANGHAI!" if score_val == "SHANGHAI!" else "FINISH (0)!"
            score_item = QTableWidgetItem(score_str)
            score_item.setForeground(QBrush(QColor("gold")))
            font = score_item.font()
            font.setBold(True)
            score_item.setFont(font)
        elif game_over and game.shanghai_variante != "Shanghai-Finish":
            # Platzierung erst anzeigen, wenn das Spiel wirklich vorbei ist!
            platz = finished_players.index(row_idx) + 1
            score_item = QTableWidgetItem(f"PLATZ {platz} ({score_val})")

            if platz == 1:
                # KORREKTUR: Nur der Sieger (Platz 1) wird fett und gold hervorgehoben!
                score_item.setForeground(QBrush(QColor("#fdbc4b")))  # Gold-gelb
                font = score_item.font()
                font.setBold(True)
                score_item.setFont(font)
            else:
                # Andere Plätze erhalten eine schlichte, nicht fette weiße Farbe
                score_item.setForeground(QBrush(QColor("white")))
        else:
            score_str = (
                f"{score_val} (Beendet)"
                if (is_finished and game.shanghai_variante != "Shanghai-Finish")
                else str(score_val)
            )
            score_item = QTableWidgetItem(score_str)
            if row_idx == current_p:
                score_item.setForeground(QBrush(QColor("gold")))
            else:
                score_item.setForeground(QBrush(QColor("white")))

        score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if row_idx == current_p:
            score_item.setBackground(QBrush(QColor("#2a2e32")))
        else:
            score_item.setBackground(QBrush(QColor("transparent")))

        table.setItem(row_idx, 4, score_item)
