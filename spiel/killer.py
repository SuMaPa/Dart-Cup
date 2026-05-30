def init_killer(game):
    # Alle starten standardmäßig mit 3 Leben
    game.scores = [3] * len(game.players)
    game.killer_numbers = [0] * len(game.players)
    game.has_entered = [True] * len(game.players)

    # Variante auslesen
    variante = game.variant_box.currentText() if hasattr(game, 'variant_box') else "Standard"
    if variante not in ["Standard", "Direkt-Killer", "Totaler Krieg"]:
        variante = "Standard"
    game.killer_variante = variante

    # Bei "Direkt-Killer" und "Totaler Krieg" startet JEDER sofort als Killer
    if game.killer_variante in ["Direkt-Killer", "Totaler Krieg"]:
        game.killer_status = [True] * len(game.players)
    else:
        game.killer_status = [False] * len(game.players)

def process_killer(game, daten):
    p = game.current_player_idx
    val = daten["val"]

    # Fehlschuss abfangen
    if val == 0:
        game.finish_dart()
        return

    # SCHRITT 1: Eigene Nummer wählen (gilt für alle Varianten)
    if game.killer_numbers[p] == 0:
        if val in game.killer_numbers or val == 25:
            if game.last_darts[p]:
                game.last_darts[p].pop()
            game.update_display()
            return
        else:
            game.killer_numbers[p] = val
            game.wait_and_next_player()
            return

    # SCHRITT 2: Im Spiel agieren
    # Wenn im Standard-Modus noch kein Killer -> Versuchen, den Status via Double zu holen
    if game.killer_variante == "Standard" and not game.killer_status[p]:
        if val == game.killer_numbers[p] and daten["was_double"]:
            game.killer_status[p] = True

    # Wenn der Spieler ein Killer ist, darf er die Gegner jagen
    elif game.killer_status[p]:
        if val in game.killer_numbers:
            g_idx = game.killer_numbers.index(val)

            if g_idx not in game.finished_players:
                # Schadensberechnung je nach Modus
                if game.killer_variante == "Totaler Krieg":
                    # Single = 1, Double = 2, Triple = 3 Leben Abzug
                    schaden = 2 if daten["was_double"] else 3 if daten["was_triple"] else 1
                    game.scores[g_idx] = max(0, game.scores[g_idx] - schaden)
                else:
                    # Standard und Direkt-Killer reagieren klassisch NUR auf das Double-Segment
                    if daten["was_double"]:
                        game.scores[g_idx] = max(0, game.scores[g_idx] - 1)

                # Prüfen, ob der getroffene Gegner eliminiert wurde
                if game.scores[g_idx] == 0:
                    game.finished_players.append(g_idx)

    # SCHRITT 3: Siegbedingung prüfen
    lebende_spieler = [i for i in range(len(game.players)) if i not in game.finished_players]
    if len(lebende_spieler) == 1:
        gewinner = lebende_spieler[0]
        # Gewinner ganz vorne in die Liste einfügen, damit Platz 1 stimmt
        if gewinner not in game.finished_players:
            game.finished_players.insert(0, gewinner)
        game.wait_and_next_player()
        return

    game.finish_dart()
