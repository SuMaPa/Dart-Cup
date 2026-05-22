ZIELE = ["20", "19", "DOUBLE", "18", "17", "TRIPLE", "BULL"]

def init_halve_it(game):
    game.scores = [40] * len(game.players)
    game.has_entered = [True] * len(game.players)
    game.round_hit = [False] * len(game.players)

def process_halve_it(game, daten):
    val = daten["val"]
    p = game.current_player_idx
    aktuelle_runde = (len(game.history) // len(game.players) // 3)
    if aktuelle_runde >= len(ZIELE):
        game.finish_dart()
        return
    ziel = ZIELE[aktuelle_runde]
    treffer = False
    if ziel == "DOUBLE" and daten["was_double"]:
        treffer = True
    elif ziel == "TRIPLE" and daten["was_triple"]:
        treffer = True
    elif ziel == "BULL" and val == 25:
        treffer = True
    elif ziel.isdigit() and val == int(ziel):
        treffer = True
    if treffer:
        game.scores[p] += daten["points"]
        game.round_hit[p] = True
    if len(game.last_darts[p]) >= 3:
        if not game.round_hit[p]:
            game.scores[p] = max(1, game.scores[p] // 2)
        game.round_hit[p] = False
        if aktuelle_runde == len(ZIELE) - 1:
            if p not in game.finished_players:
                game.finished_players.append(p)

    game.finish_dart()
