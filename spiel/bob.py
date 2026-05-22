def init_bobs27(app):

    app.game_mode = "Bob's 27"
    app.scores = [27] * len(app.players)
    app.bobs_target = [1] * len(app.players)
    app.bobs_hit_in_turn = False

def zuruecksetzen_falls_raus(app, spieler_idx):
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
        if app.scores[p] > 0:
            if app.bobs_target[p] < 20:
                app.bobs_target[p] += 1
            elif app.bobs_target[p] == 20:
                app.bobs_target[p] = 25
            else:
                if p not in app.finished_players:
                    app.finished_players.append(p)

    app.finish_dart()
