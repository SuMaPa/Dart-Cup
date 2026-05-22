def init_shanghai(game):
    game.scores = [0] * len(game.players)
    game.has_entered = [True] * len(game.players)
    game.round_modifiers = [set() for _ in range(len(game.players))]

def process_shanghai(game, daten):
    val = daten["val"]
    p = game.current_player_idx
    aktuelle_runde = (len(game.history) // len(game.players) // 3) + 1
    if aktuelle_runde > 7:
        game.finish_dart()
        return
    if val == aktuelle_runde:
        modifier = daten.get("points", val) // val if val > 0 else 1
        game.scores[p] += daten["points"]
        game.round_modifiers[p].add(modifier)
        if {1, 2, 3}.issubset(game.round_modifiers[p]):
            game.scores[p] = "SHANGHAI!"
            game.finished_players.append(p)
            game.darts_thrown += 1
            game.wait_and_next_player()
            return
    if game.darts_thrown == 2:
        game.round_modifiers[p] = set()
        if aktuelle_runde == 7:
            if p not in game.finished_players:
                game.finished_players.append(p)

    game.finish_dart()
