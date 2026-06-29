# spiel/shanghai.py


def init_shanghai(game):
    # Variante auslesen
    variante = (
        game.variant_box.currentText() if hasattr(game, "variant_box") else "Standard"
    )
    game.shanghai_variante = variante

    # Start-Punkte initialisieren (Shanghai-Finish startet bei 120, andere bei 0)
    if game.shanghai_variante == "Shanghai-Finish":
        game.scores = [120] * len(game.players)
    else:
        game.scores = [0] * len(game.players)

    game.has_entered = [True] * len(game.players)

    # Trackt, welche Segmente (Single=1, Double=2, Triple=3) in der aktuellen Runde getroffen wurden
    game.round_modifiers = [set() for _ in range(len(game.players))]


def process_shanghai(game, daten):
    val = daten["val"]
    points = daten["points"]
    p = game.current_player_idx
    aktuelle_runde = getattr(game, "current_round", 1)

    # Im Shanghai-Finish werfen wir immer auf die 20, ansonsten auf die Runden-Zahl
    ziel_zahl = 20 if game.shanghai_variante == "Shanghai-Finish" else aktuelle_runde

    # Prüfen, ob das Spiel vorbei ist (nach Runde 20 für Standard/Double-Only)
    if game.shanghai_variante != "Shanghai-Finish" and aktuelle_runde > 20:
        if p not in game.finished_players:
            game.finished_players.append(p)
        game.wait_and_next_player()
        return

    is_hit = False
    if val == ziel_zahl:
        if game.shanghai_variante == "Double-Only":
            # Bei Double-Only bringen nur Double-Felder Punkte
            if daten["was_double"]:
                is_hit = True
        else:
            is_hit = True

    if is_hit:
        # Punkte verbuchen
        if game.shanghai_variante == "Shanghai-Finish":
            new_score = game.scores[p] - points
            if new_score == 0 and daten["was_double"]:
                # Exaktes Finish auf Null mit einem Doppel-Feld geschafft!
                game.scores[p] = 0
                game.finished_players.append(p)
                game.wait_and_next_player()
                return
            elif (
                new_score < 0
                or (new_score == 1)
                or (new_score == 0 and not daten["was_double"])
            ):
                # Bust (Überworfen, verbleibender Rest von 1 oder Null ohne Doppel-Finish)
                pass
            else:
                game.scores[p] = new_score
        else:
            # Standard & Double-Only sammeln Pluspunkte
            game.scores[p] += points

        # Modifikatoren-Prüfung für den Shanghai-Sofortsieg (S, D, T in einer Runde)
        if game.shanghai_variante in ["Standard", "Shanghai-Finish"]:
            modifier = points // val if val > 0 else 1
            game.round_modifiers[p].add(modifier)

            # Haben wir Single (1), Double (2) und Triple (3) der Zielzahl im Board?
            if {1, 2, 3}.issubset(game.round_modifiers[p]):
                game.scores[p] = "SHANGHAI!"
                game.finished_players.append(p)
                game.wait_and_next_player()
                return

    if len(game.last_darts[p]) >= 3:
        # Modifikatoren am Rundenende zurücksetzen
        game.round_modifiers[p] = set()

        if game.shanghai_variante == "Shanghai-Finish":
            # Wenn nach dem 3. Dart kein Finish geschafft wurde, wird die Aufnahme zurückgesetzt
            if game.scores[p] != 0:
                game.scores[p] = 120
        else:
            # Turn-Ende bei Standard / Double-Only in Runde 20
            if aktuelle_runde == 20:
                if p not in game.finished_players:
                    game.finished_players.append(p)

                # Wenn alle Spieler durch sind, sortieren wir das Endklassement
                alle_fertig = len(game.finished_players) >= len(game.players)
                if alle_fertig:
                    score_pairs = [
                        (idx, game.scores[idx]) for idx in range(len(game.players))
                    ]
                    score_pairs.sort(key=lambda x: x[1], reverse=True)
                    game.finished_players = [pair[0] for pair in score_pairs]
                    # Auch hier kein vorzeitiger Abbruch mehr!

    game.finish_dart()
