# ui/spiel/halve_it.py
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
    layout.addWidget(QLabel("<b>Auswertung: Halve It</b>"))
    layout.addWidget(QLabel(f"Gewinner: {match_data.get('gewinner', 'N/A')}"))
    layout.addStretch()
    scroll.setWidget(w)
    return scroll


def get_live_widget(game):
    table = QTableWidget()
    table.setRowCount(len(game.players))
    table.setColumnCount(6)  # Spieler | Rundenziel | Dart 1 | Dart 2 | Dart 3 | Score
    table.setHorizontalHeaderLabels(
        ["Spieler", "Rundenziel", "Dart 1", "Dart 2", "Dart 3", "Score"]
    )
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
    aktuelle_runde = getattr(game, "current_round", 1) - 1
    targets = getattr(game, "halve_it_targets", [])

    # Das Spiel ist erst komplett vorbei, wenn alle Spieler fertiggespielt haben
    game_over = len(finished_players) >= len(game.players)

    translations = {
        "DOUBLE": "Beliebiges Doppel",
        "TRIPLE": "Beliebiges Triple",
        "BULL": "Bull (25/50)",
        "BULLSEYE": "Rotes Bull (50)",
        "ROT": "Rotes Feld",
        "3_FARBEN": "3 versch. Farben",
        "SCORING": "Punkte sammeln!",
        "T20": "Triple 20",
        "D20": "Double 20",
    }

    if aktuelle_runde < len(targets):
        ziel_raw = targets[aktuelle_runde]
        ziel_str = translations.get(ziel_raw, f"Feld {ziel_raw}")
    else:
        ziel_str = "Beendet"

    for row_idx, player_name in enumerate(game.players):
        is_finished = row_idx in finished_players

        # 1. Spalte: Spielername
        name_item = QTableWidgetItem(player_name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if row_idx == current_p and not is_finished:
            name_item.setForeground(QBrush(QColor("gold")))
            name_item.setBackground(QBrush(QColor("#2a2e32")))
        else:
            name_item.setBackground(QBrush(QColor("transparent")))
            name_item.setForeground(QBrush(QColor("white")))

        table.setItem(row_idx, 0, name_item)

        # 2. Spalte: Rundenziel
        p_ziel_str = ziel_str if not is_finished else "Beendet"
        ziel_item = QTableWidgetItem(p_ziel_str)
        ziel_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if row_idx == current_p and not is_finished:
            ziel_item.setBackground(QBrush(QColor("#2a2e32")))
            ziel_item.setForeground(QBrush(QColor("#3daee9")))
            font = ziel_item.font()
            font.setBold(True)
            ziel_item.setFont(font)
        else:
            ziel_item.setBackground(QBrush(QColor("transparent")))
            ziel_item.setForeground(QBrush(QColor("gray")))

        table.setItem(row_idx, 1, ziel_item)

        # 3., 4., 5. Spalte: Darts (Dart 1, Dart 2, Dart 3)
        thrown = game.last_darts[row_idx] if row_idx < len(game.last_darts) else []
        for d_idx in range(3):
            val_str = thrown[d_idx] if d_idx < len(thrown) else ""
            item = QTableWidgetItem(val_str)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if row_idx == current_p and not is_finished:
                item.setBackground(QBrush(QColor("#2a2e32")))
                item.setForeground(QBrush(QColor("#3daee9")))
            else:
                item.setBackground(QBrush(QColor("transparent")))
                item.setForeground(QBrush(QColor("white")))

            table.setItem(row_idx, d_idx + 2, item)

        # 6. Spalte: Score (Gesamtpunkte)
        score_val = game.scores[row_idx]

        if game_over:
            # Platzierung erst anzeigen, wenn das Spiel tatsächlich beendet ist!
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
            # Während des Spiels bleibt die normale Punkteanzeige
            score_str = f"{score_val} (Beendet)" if is_finished else str(score_val)
            score_item = QTableWidgetItem(score_str)
            if row_idx == current_p:
                score_item.setForeground(QBrush(QColor("gold")))
                font = score_item.font()
                font.setBold(True)
                score_item.setFont(font)
            else:
                score_item.setForeground(QBrush(QColor("white")))

        score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if row_idx == current_p and not is_finished:
            score_item.setBackground(QBrush(QColor("#2a2e32")))
        else:
            score_item.setBackground(QBrush(QColor("transparent")))

        table.setItem(row_idx, 5, score_item)
