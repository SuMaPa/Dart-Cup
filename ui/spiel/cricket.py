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


def init_cricket(game):
    game.scores = [0] * len(game.players)
    game.cricket_stat = {
        player_idx: {num: 0 for num in [15, 16, 17, 18, 19, 20, 25]}
        for player_idx in range(len(game.players))
    }
    game.has_entered = [True] * len(game.players)
    variante = (
        game.variant_box.currentText() if hasattr(game, "variant_box") else "Standard"
    )
    if variante not in ["Standard", "Cut-Throat", "No-Score"]:
        variante = "Standard"
    game.cricket_variante = variante


def process_cricket(game, daten):
    print(f"DEBUG: process_cricket wurde aufgerufen mit {daten}")
    val = daten["val"]
    p = game.current_player_idx
    modifier = daten["points"] // val if val > 0 else 1

    if val in game.cricket_stat[p]:
        for _ in range(modifier):
            if game.cricket_stat[p][val] < 3:
                game.cricket_stat[p][val] += 1
            else:
                gegner_haben_offen = any(
                    game.cricket_stat[g_idx][val] < 3
                    for g_idx in range(len(game.players))
                    if g_idx != p
                )
                if gegner_haben_offen:
                    punkte_wert = 25 if val == 25 else val
                    if game.cricket_variante == "Standard":
                        game.scores[p] += punkte_wert
                    elif game.cricket_variante == "Cut-Throat":
                        for g_idx in range(len(game.players)):
                            if g_idx != p and game.cricket_stat[g_idx][val] < 3:
                                game.scores[g_idx] += punkte_wert
                    elif game.cricket_variante == "No-Score":
                        pass

        alles_zu = all(game.cricket_stat[p][num] == 3 for num in game.cricket_stat[p])
        if alles_zu:
            if game.cricket_variante == "Standard" and game.scores[p] == max(
                game.scores
            ):
                game.finished_players.append(p)
                game.wait_and_next_player()
                return
            elif game.cricket_variante == "Cut-Throat" and game.scores[p] == min(
                game.scores
            ):
                game.finished_players.append(p)
                game.wait_and_next_player()
                return
            elif game.cricket_variante == "No-Score":
                game.finished_players.append(p)
                game.wait_and_next_player()
                return
    game.finish_dart()


def get_stats_widget(match_data):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    w = QWidget()
    layout = QVBoxLayout(w)
    layout.addWidget(QLabel("<b>Auswertung: Cricket</b>"))
    layout.addWidget(QLabel(f"Dominator: {match_data.get('gewinner', 'N/A')}"))
    layout.addStretch()
    scroll.setWidget(w)
    return scroll


def get_live_widget(game):
    table = QTableWidget()
    # Wir packen "Spieler" als echte erste Spalte rein
    headers = ["Spieler", "20", "19", "18", "17", "16", "15", "BULL", "Score"]
    table.setRowCount(len(game.players))
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)

    # Den nutzlosen, nativen vertikalen Header ausblenden
    table.verticalHeader().setVisible(False)

    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    update_live_widget(game, table)
    return table


def update_live_widget(game, table):
    from PyQt6.QtGui import QColor, QBrush

    numbers = [20, 19, 18, 17, 16, 15, 25]
    symbols = {0: "", 1: "/", 2: "X", 3: "O"}
    current_p = game.current_player_idx

    for row_idx, player_name in enumerate(game.players):
        # 1. Spielername in Spalte 0 (hier funktioniert Gold einwandfrei!)
        name_item = QTableWidgetItem(player_name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if row_idx == current_p:
            name_item.setForeground(QBrush(QColor("gold")))
            name_item.setBackground(QBrush(QColor("#2a2e32")))
        else:
            name_item.setBackground(QBrush(QColor("transparent")))
        table.setItem(row_idx, 0, name_item)

        # 2. Cricket-Symbole (Verschoben auf Spalte 1 bis 7)
        for col_idx, num in enumerate(numbers):
            hit_count = game.cricket_stat.get(row_idx, {}).get(num, 0)
            val = symbols.get(hit_count, "")

            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if row_idx == current_p:
                item.setBackground(QBrush(QColor("#2a2e32")))
            else:
                item.setBackground(QBrush(QColor("transparent")))

            table.setItem(row_idx, col_idx + 1, item)  # +1 wegen der Spieler-Spalte

        # 3. Score-Eintrag (Jetzt in Spalte 8)
        score_item = QTableWidgetItem(str(game.scores[row_idx]))
        score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if row_idx == current_p:
            score_item.setBackground(QBrush(QColor("#2a2e32")))
        table.setItem(row_idx, 8, score_item)
