from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea


def init_around_the_clock(game):
    game.scores = [1] * len(game.players)
    variante = (
        game.variant_box.currentText() if hasattr(game, "variant_box") else "Standard"
    )
    game.clock_variante = (
        variante if variante in ["Standard", "Double-Only", "All-In"] else "Standard"
    )


def process_around_the_clock(game, daten):
    val = daten["val"]
    p = game.current_player_idx
    target = game.scores[p]

    is_hit = False
    schritte = 0

    if game.clock_variante == "Standard" and val == target:
        is_hit, schritte = True, 1
    elif game.clock_variante == "Double-Only" and val == target and daten["was_double"]:
        is_hit, schritte = True, 1
    elif game.clock_variante == "All-In" and val == target:
        is_hit = True
        if daten["was_triple"]:
            schritte = 3
        elif daten["was_double"]:
            schritte = 2
        else:
            schritte = 1

    if is_hit:
        neuer_score = target + schritte
        game.scores[p] = 25 if neuer_score > 20 else neuer_score

    if game.scores[p] == 25 and val == 25:
        game.scores[p] = 0
        game.finished_players.append(p)
        game.wait_and_next_player()
        return

    game.finish_dart()


def get_stats_widget(match_data):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    w = QWidget()
    layout = QVBoxLayout(w)
    layout.addWidget(QLabel("<b>Auswertung: Around the Clock</b>"))
    layout.addWidget(QLabel(f"Zeitherrscher: {match_data.get('gewinner', 'N/A')}"))
    layout.addStretch()
    scroll.setWidget(w)
    return scroll
