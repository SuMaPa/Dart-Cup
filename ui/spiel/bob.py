# ui/spiel/bob.py
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
from PyQt6.QtGui import QColor, QBrush

BOB_START_PUNKTE = {"Classic": 27, "Einsteiger": 50, "Open End": 27}


def init_bobs27(app):
    from dart_cup import SPIEL_MODI

    for mode_name, mode_tuple in SPIEL_MODI.items():
        if mode_tuple[0] == spiel_bobs27:
            app.game_mode = mode_name
            break
    variante = (
        app.variant_box.currentText() if hasattr(app, "variant_box") else "Classic"
    )
    if variante not in BOB_START_PUNKTE:
        variante = "Classic"
    app.bobs_variante = variante
    app.scores = [BOB_START_PUNKTE[variante]] * len(app.players)
    app.bobs_target = [1] * len(app.players)
    app.bobs_hit_in_turn = False
    app.bobs_stat = {
        player_idx: {
            t: 0
            for t in [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                25,
            ]
        }
        for player_idx in range(len(app.players))
    }


def zuruecksetzen_falls_raus(app, spieler_idx):
    if app.bobs_variante != "Open End":
        if app.scores[spieler_idx] <= 0:
            app.scores[spieler_idx] = 0
            if spieler_idx not in app.finished_players:
                app.finished_players.append(spieler_idx)
                app.is_bust[spieler_idx] = True


def spiel_bobs27(app, daten):
    p = app.current_player_idx
    target = app.bobs_target[p]

    if p in app.finished_players:
        app.finish_dart()
        return

    if app.darts_thrown == 0:
        app.bobs_hit_in_turn = False

    ist_treffer = False
    if target == 25:
        if daten["val"] == 25 and daten["was_double"]:
            ist_treffer = True
    else:
        if daten["val"] == target and daten["was_double"]:
            ist_treffer = True

    if ist_treffer:
        app.scores[p] += target * 2
        app.bobs_hit_in_turn = True
        if target in app.bobs_stat[p]:
            app.bobs_stat[p][target] += 1

    if len(app.last_darts[p]) >= 3:
        if not app.bobs_hit_in_turn:
            app.scores[p] -= target * 2
        zuruecksetzen_falls_raus(app, p)

        if app.scores[p] > 0 or app.bobs_variante == "Open End":
            if app.bobs_target[p] < 20:
                app.bobs_target[p] += 1
            elif app.bobs_target[p] == 20:
                app.bobs_target[p] = 25
            else:
                if p not in app.finished_players:
                    app.finished_players.append(p)

    app.finish_dart()


def get_stats_widget(match_data):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    w = QWidget()
    layout = QVBoxLayout(w)
    layout.addWidget(QLabel("<b>Auswertung: Bob's 27</b>"))
    layout.addWidget(QLabel(f"Gewinner: {match_data.get('gewinner', 'N/A')}"))
    layout.addStretch()
    scroll.setWidget(w)
    return scroll


def get_live_widget(game):
    table = QTableWidget()
    table.setRowCount(len(game.players))
    table.setColumnCount(8)  # Spielername + 6 Runden (5 vorherige + 1 aktuelle) + Score
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    update_live_widget(game, table)
    return table


def update_live_widget(game, table):
    TARGETS = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        25,
    ]
    current_p = game.current_player_idx
    active_target = getattr(game, "bobs_target", [1] * len(game.players))[current_p]

    try:
        idx = TARGETS.index(active_target)
    except ValueError:
        idx = 0

    # Schiebe-Fenster: Am Anfang zeigen wir D1 bis D6 (damit die Tabelle immer gleich breit bleibt).
    # Sobald wir weiter fortgeschritten sind, zeigen wir die 5 vorherigen + das aktuelle Ziel.
    if idx < 5:
        visible_targets = TARGETS[0:6]
    else:
        visible_targets = TARGETS[idx - 5 : idx + 1]

    # Spaltenköpfe setzen
    headers = (
        ["Spieler"]
        + [f"D{t}" if t != 25 else "D-BULL" for t in visible_targets]
        + ["Score"]
    )
    table.setHorizontalHeaderLabels(headers)

    symbols = {0: "-", 1: "/", 2: "X", 3: "O"}

    for row_idx, player_name in enumerate(game.players):
        # 1. Spieler-Name
        name_item = QTableWidgetItem(player_name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if row_idx == current_p:
            name_item.setForeground(QBrush(QColor("gold")))
            name_item.setBackground(QBrush(QColor("#2a2e32")))
        else:
            name_item.setBackground(QBrush(QColor("transparent")))
        table.setItem(row_idx, 0, name_item)

        # 2. Die Runden-Symbole
        player_target = getattr(game, "bobs_target", [1] * len(game.players))[row_idx]
        player_stat = getattr(game, "bobs_stat", {}).get(row_idx, {})

        for col_idx, t in enumerate(visible_targets):
            if t > player_target:
                # Zukünftiges Segment für diesen Spieler -> leer lassen
                val_str = ""
            else:
                # Aktuelles oder bereits geworfenes Segment
                hit_count = player_stat.get(t, 0)
                val_str = symbols.get(hit_count, "-")

            item = QTableWidgetItem(val_str)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if row_idx == current_p:
                item.setBackground(QBrush(QColor("#2a2e32")))
                if t == player_target:
                    # Das gerade aktive Ziel des aktuellen Spielers farbig markieren
                    item.setForeground(QBrush(QColor("#3daee9")))
            else:
                item.setBackground(QBrush(QColor("transparent")))

            table.setItem(row_idx, col_idx + 1, item)

        # 3. Score-Eintrag
        score_val = game.scores[row_idx]
        is_bust = game.is_bust[row_idx] if hasattr(game, "is_bust") else False

        if is_bust or score_val <= 0:
            score_item = QTableWidgetItem("BUST")
            score_item.setForeground(QBrush(QColor("#ff4c4c")))
        else:
            score_item = QTableWidgetItem(str(score_val))
            if row_idx == current_p:
                score_item.setForeground(QBrush(QColor("gold")))

        score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if row_idx == current_p:
            score_item.setBackground(QBrush(QColor("#2a2e32")))
        else:
            score_item.setBackground(QBrush(QColor("transparent")))
        table.setItem(
            row_idx, 7, score_item
        )  # Jetzt Spalte 7, da wir insgesamt 8 Spalten haben
