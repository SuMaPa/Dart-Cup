# Schwierigkeitsgrade direkt hier definiert
BOB_START_PUNKTE = {
    "Classic": 27,
    "Einsteiger": 50,
    "Open End": 27
}

def init_bobs27(app):
    # Bestehende Logik für den Modus-Namen
    from dart_cup import SPIEL_MODI
    for mode_name, mode_tuple in SPIEL_MODI.items():
        if mode_tuple[0] == spiel_bobs27:
            app.game_mode = mode_name
            break

    # Variante auslesen
    variante = app.variant_box.currentText() if hasattr(app, 'variant_box') else "Classic"
    if variante not in BOB_START_PUNKTE:
        variante = "Classic"

    app.bobs_variante = variante
    app.scores = [BOB_START_PUNKTE[variante]] * len(app.players)
    app.bobs_target = [1] * len(app.players)
    app.bobs_hit_in_turn = False

def zuruecksetzen_falls_raus(app, spieler_idx):
    # Nur bei Classic und Einsteiger fliegt man bei 0 raus
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
        app.scores[p] += (target * 2)
        app.bobs_hit_in_turn = True

    if len(app.last_darts[p]) >= 3:
        if not app.bobs_hit_in_turn:
            app.scores[p] -= (target * 2)

        zuruecksetzen_falls_raus(app, p)

        # Weiterspielen nur, wenn nicht bust (außer bei Open End)
        if app.scores[p] > 0 or app.bobs_variante == "Open End":
            if app.bobs_target[p] < 20:
                app.bobs_target[p] += 1
            elif app.bobs_target[p] == 20:
                app.bobs_target[p] = 25
            else:
                if p not in app.finished_players:
                    app.finished_players.append(p)

    app.finish_dart()
