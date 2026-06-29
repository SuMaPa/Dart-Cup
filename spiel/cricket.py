def init_cricket(game):
    game.scores = [0] * len(game.players)
    game.cricket_stat = {
        player_idx: {num: 0 for num in [15, 16, 17, 18, 19, 20, 25]}
        for player_idx in range(len(game.players))
    }
    game.has_entered = [True] * len(game.players)

    # Variante aus der UI auslesen
    variante = (
        game.variant_box.currentText() if hasattr(game, "variant_box") else "Standard"
    )
    if variante not in ["Standard", "Cut-Throat", "No-Score"]:
        variante = "Standard"
    game.cricket_variante = variante


def process_cricket(game, daten):
    val = daten["val"]
    p = game.current_player_idx

    # Ermitteln, wie viele Treffer dieser Wurf zählt (Single=1, Double=2, Triple=3)
    modifier = daten["points"] // val if val > 0 else 1

    if val in game.cricket_stat[p]:
        treffer_zufuhr = modifier
        for _ in range(treffer_zufuhr):
            # 1. Wenn das Feld noch nicht 3-mal getroffen wurde, wird es weiter geschlossen
            if game.cricket_stat[p][val] < 3:
                game.cricket_stat[p][val] += 1

            # 2. Wenn das Feld bereits geschlossen ist, prüfen wir die Punktevergabe
            else:
                # Prüfen, ob es noch Gegner gibt, die das Feld offen haben
                gegner_haben_offen = any(
                    game.cricket_stat[g_idx][val] < 3
                    for g_idx in range(len(game.players))
                    if g_idx != p
                )

                if gegner_haben_offen:
                    punkte_wert = 25 if val == 25 else val

                    if game.cricket_variante == "Standard":
                        # Standard: Punkte gehen auf das eigene Konto
                        game.scores[p] += punkte_wert

                    elif game.cricket_variante == "Cut-Throat":
                        # Cut-Throat: Punkte gehen an ALLE Gegner, die das Feld NOCH OFFEN haben
                        for g_idx in range(len(game.players)):
                            if g_idx != p and game.cricket_stat[g_idx][val] < 3:
                                game.scores[g_idx] += punkte_wert

                    elif game.cricket_variante == "No-Score":
                        # No-Score: Es werden schlicht keine Punkte vergeben
                        pass

        # Siegbedingung ermitteln: Alle Felder müssen geschlossen sein (3er-Status)
        alles_zu = all(game.cricket_stat[p][num] == 3 for num in game.cricket_stat[p])

        if alles_zu:
            if game.cricket_variante == "Standard":
                # Standard-Sieg: Alles zu + die MEISTEN Punkte
                if game.scores[p] == max(game.scores):
                    game.finished_players.append(p)
                    game.wait_and_next_player()
                    return

            elif game.cricket_variante == "Cut-Throat":
                # Cut-Throat-Sieg: Alles zu + die WENIGSTEN Punkte
                if game.scores[p] == min(game.scores):
                    game.finished_players.append(p)
                    game.wait_and_next_player()
                    return

            elif game.cricket_variante == "No-Score":
                # No-Score-Sieg: Wer zuerst alles zu hat, gewinnt sofort
                game.finished_players.append(p)
                game.wait_and_next_player()
                return

    game.finish_dart()
