# spiel/halve_it.py

HALVE_IT_VARIANTEN = {
    "Standard": ["15", "16", "DOUBLE", "17", "18", "TRIPLE", "19", "20", "BULL"],
    "Kurz": ["15", "16", "17", "18", "19", "20"],
    "Pro Challenge": [
        "SCORING",
        "TRIPLE",
        "DOUBLE",
        "ROT",
        "T20",
        "D20",
        "3_FARBEN",
        "BULLSEYE",
    ],
}


def get_dart_color(val, multiplier):
    """Ermittelt die exakte Farbe eines getroffenen Feldes auf einem Standard-Board."""
    if val == 25:
        return (
            "Green" if multiplier == 1 else "Red"
        )  # Outer Bull = Grün, Bullseye = Rot

    # Zahlen, deren Doubles und Triples auf einem Standardboard ROT eingefärbt sind
    red_green_nums = [20, 18, 13, 10, 2, 3, 7, 8, 12, 14]
    if multiplier in [2, 3]:
        return "Red" if val in red_green_nums else "Green"
    else:
        # Single-Flächen sind abwechselnd Schwarz und Weiß
        return "Black" if val in red_green_nums else "White"


def init_halve_it(game):
    variante = (
        game.variant_box.currentText() if hasattr(game, "variant_box") else "Standard"
    )
    if variante not in HALVE_IT_VARIANTEN:
        variante = "Standard"
    game.halve_it_variante = variante
    game.halve_it_targets = HALVE_IT_VARIANTEN[variante]

    # Pro Challenge startet bei 0 (Sammelrunde), andere traditionell bei 40 Startpunkten
    start_score = 0 if variante == "Pro Challenge" else 40
    game.scores = [start_score] * len(game.players)
    game.has_entered = [True] * len(game.players)

    # Trackt, ob in dieser Runde mindestens ein Treffer erzielt wurde
    game.round_hit = [False] * len(game.players)

    # Für Pro Challenge Runde 7 (3 verschiedene Farben)
    game.round_colors = [set() for _ in range(len(game.players))]


def process_halve_it(game, daten):
    val = daten["val"]
    points = daten["points"]
    p = game.current_player_idx
    aktuelle_runde = getattr(game, "current_round", 1) - 1

    if aktuelle_runde >= len(game.halve_it_targets):
        game.finish_dart()
        return

    ziel = game.halve_it_targets[aktuelle_runde]
    treffer = False

    # Farbe und Modifikator ermitteln
    mult = points // val if val > 0 else 1
    color = get_dart_color(val, mult)

    if ziel == "SCORING":
        if val > 0:
            treffer = True  # Jeder Treffer auf der Scheibe zählt
    elif ziel == "DOUBLE" and daten["was_double"]:
        treffer = True
    elif ziel == "TRIPLE" and daten["was_triple"]:
        treffer = True
    elif ziel == "BULL" and val == 25:
        treffer = True  # Bullseye (50) und Outer Bull (25) zählen
    elif ziel == "BULLSEYE" and val == 25 and daten["was_double"]:
        treffer = True  # Nur das rote Zentrum (50) zählt
    elif ziel == "ROT" and color == "Red":
        treffer = True
    elif ziel == "T20" and val == 20 and daten["was_triple"]:
        treffer = True
    elif ziel == "D20" and val == 20 and daten["was_double"]:
        treffer = True
    elif ziel == "3_FARBEN" and val > 0:
        game.round_colors[p].add(color)
        treffer = True
    elif ziel.isdigit() and val == int(ziel):
        treffer = True

    if treffer:
        game.scores[p] += points
        game.round_hit[p] = True

    if len(game.last_darts[p]) >= 3:
        gescheitert = False

        if ziel == "3_FARBEN":
            # Wurden am Rundenende nicht mindestens 3 verschiedene Farben getroffen -> gescheitert!
            if len(game.round_colors[p]) < 3:
                gescheitert = True
            game.round_colors[p] = set()
        else:
            if not game.round_hit[p]:
                gescheitert = True

        if gescheitert:
            # Strafe: Punkte halbieren (nicht unter 1 fallen lassen) [cite: 2.1.1]
            game.scores[p] = max(1, game.scores[p] // 2)

        game.round_hit[p] = False

        # Turn-Ende registrieren
        if aktuelle_runde == len(game.halve_it_targets) - 1:
            if p not in game.finished_players:
                game.finished_players.append(p)

            # Wenn alle fertig sind, Spiel beenden und Klassement sortieren
            alle_fertig = len(game.finished_players) >= len(game.players)
            if alle_fertig:
                score_pairs = [
                    (idx, game.scores[idx]) for idx in range(len(game.players))
                ]
                score_pairs.sort(key=lambda x: x[1], reverse=True)
                game.finished_players = [pair[0] for pair in score_pairs]
                # Kein vorzeitiger Abbruch/Return mehr! game.finish_dart() regelt den Abschluss sauber.

    game.finish_dart()
