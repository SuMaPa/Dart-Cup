from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea


def init_classic(game):
    start_score = (
        int(game.variant_box.currentText()) if hasattr(game, "variant_box") else 301
    )
    game.scores = [start_score] * len(game.players)
    game.has_entered = [not game.cb_double_in.isChecked()] * len(game.players)


def process_classic(game, daten):
    val = daten["val"]
    points = daten["points"]
    was_double = daten["was_double"]
    p = game.current_player_idx

    if not game.has_entered[p]:
        if was_double:
            game.has_entered[p] = True
        else:
            game.finish_dart()
            return

    new_score = game.scores[p] - points
    if new_score == 0 and (not game.double_out or was_double):
        game.scores[p] = 0
        game.finished_players.append(p)
        game.wait_and_next_player()
        return

    if (
        (new_score < 0)
        or (new_score == 1 and game.double_out)
        or (new_score == 0 and game.double_out and not was_double)
    ):
        game.scores[p] = game.score_at_start_of_turn
        game.is_bust[p] = True
        game.darts_thrown += 1
        game.wait_and_next_player()
        return

    game.scores[p] = new_score
    game.finish_dart()


def get_stats_widget(match_data):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    w = QWidget()
    layout = QVBoxLayout(w)

    layout.addWidget(QLabel("<b>Auswertung: Classic X01</b>"))
    layout.addWidget(QLabel(f"Gewinner: {match_data.get('gewinner', 'N/A')}"))

    # Beispiel für X01-spezifische Auswertung
    wuerfe = len(match_data.get("verlauf", []))
    layout.addWidget(QLabel(f"Gesamte Darts im Match: {wuerfe}"))

    layout.addStretch()
    scroll.setWidget(w)
    return scroll
