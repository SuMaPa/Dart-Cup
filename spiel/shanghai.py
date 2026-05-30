def init_shanghai(game):
    game.scores = [0] * len(game.players)
    game.has_entered = [True] * len(game.players)
    game.round_modifiers = [set() for _ in range(len(game.players))]
    # Variante aus der UI
    variante = game.variant_box.currentText() if hasattr(game, 'variant_box') else "Standard"
    game.shanghai_variante = variante

def process_shanghai(game, daten):
    val = daten["val"]
    p = game.current_player_idx
    # Annahme: 20 Runden bei Standard, sonst kürzer/speziell
    aktuelle_runde = (len(game.history) // len(game.players) // 3) + 1

    if aktuelle_runde > 20:
        game.finished_players.append(p)
        game.wait_and_next_player()
        return

    is_hit = False
    if val == aktuelle_runde:
        # Prüfung auf Double-Only
        if game.shanghai_variante == "Double-Only":
            if daten["was_double"]:
                is_hit = True
        else:
            is_hit = True

    if is_hit:
        game.scores[p] += daten["points"]
        # Nur bei "Shanghai-Finish" sammeln wir Modifier für den Sofort-Sieg
        if game.shanghai_variante == "Shanghai-Finish":
            modifier = daten["points"] // val if val > 0 else 1
            game.round_modifiers[p].add(modifier)
            if {1, 2, 3}.issubset(game.round_modifiers[p]):
                game.scores[p] = "SHANGHAI!"
                game.finished_players.append(p)
                game.wait_and_next_player()
                return

    if game.darts_thrown == 2:
        game.round_modifiers[p] = set()
        if aktuelle_runde == 20:
            if p not in game.finished_players:
                game.finished_players.append(p)
                game.wait_and_next_player()
                return

    game.finish_dart()
