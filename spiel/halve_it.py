# Direkt hier definiert, um den zirkulären Import zu killen
HALVE_IT_VARIANTEN = {
    "Standard": ["12", "13", "14", "DOUBLE", "15", "16", "17", "DOUBLE", "18", "19", "20", "BULL"],
    "Kurz": ["20", "19", "DOUBLE", "18", "17", "TRIPLE", "BULL"],
    "Pro Challenge": ["15", "DOUBLE", "16", "17", "18", "TRIPLE", "19", "20", "BULL"]
}

def init_halve_it(game):
    game.scores = [40] * len(game.players)
    game.has_entered = [True] * len(game.players)
    game.round_hit = [False] * len(game.players)

    variante = game.variant_box.currentText() if hasattr(game, 'variant_box') else "Standard"
    if variante not in HALVE_IT_VARIANTEN:
        variante = "Standard"

    game.halve_it_targets = HALVE_IT_VARIANTEN[variante]

def process_halve_it(game, daten):
    val = daten["val"]
    p = game.current_player_idx

    aktuelle_runde = (len(game.history) // len(game.players) // 3)

    if aktuelle_runde >= len(game.halve_it_targets):
        game.finish_dart()
        return

    ziel = game.halve_it_targets[aktuelle_runde]
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

        if aktuelle_runde == len(game.halve_it_targets) - 1:
            if p not in game.finished_players:
                game.finished_players.append(p)

    game.finish_dart()
