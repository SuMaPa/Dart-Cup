# spiel/killer.py


def init_killer(game):
    # Variante auslesen
    variante = (
        game.variant_box.currentText() if hasattr(game, "variant_box") else "Standard"
    )
    if variante not in ["Standard", "Direkt-Killer", "Totaler Krieg"]:
        variante = "Standard"
    game.killer_variante = variante

    # Start-Leben festlegen
    if game.killer_variante in ["Direkt-Killer", "Totaler Krieg"]:
        game.scores = [3] * len(game.players)
    else:
        game.scores = [0] * len(game.players)  # Standard startet mit 0 Leben

    game.killer_numbers = [0] * len(game.players)
    game.has_entered = [True] * len(game.players)

    # Sonderoptionen laden
    game.double_in = (
        game.cb_double_in.isChecked() if hasattr(game, "cb_double_in") else False
    )
    game.double_out = (
        game.cb_double_out.isChecked() if hasattr(game, "cb_double_out") else False
    )

    # Trackt, ob der Double-In-Wurf für den Spielstart erfolgt ist (für Standard-Modus)
    game.double_in_done = [not game.double_in] * len(game.players)

    # Killer-Status beim Start definieren
    if game.killer_variante == "Totaler Krieg":
        game.killer_status = [True] * len(game.players)
    elif game.killer_variante == "Direkt-Killer":
        # Bei Direkt-Killer mit Double-In startet der Killer-Status gesperrt (False)
        if game.double_in:
            game.killer_status = [False] * len(game.players)
        else:
            game.killer_status = [True] * len(game.players)
    else:
        # Standard-Modus startet immer ohne Killer-Status
        game.killer_status = [False] * len(game.players)


def process_killer(game, daten):
    p = game.current_player_idx
    val = daten["val"]

    # Fehlschuss abfangen
    if val == 0:
        game.finish_dart()
        return

    # SCHRITT 1: Eigene Nummer wählen (gilt für alle Varianten)
    # Jede Zahl darf nur einmal vergeben werden und Bullseye (25) ist gesperrt
    if game.killer_numbers[p] == 0:
        if val in game.killer_numbers or val == 25:
            # Ungültige Zahl: Wurf aus der Dart-Anzeige löschen
            if game.last_darts[p]:
                game.last_darts[p].pop()
            game.update_display()
            return
        else:
            # Zahl erfolgreich reserviert, Turn endet sofort
            game.killer_numbers[p] = val
            game.wait_and_next_player()
            return

    # Wenn der Spieler bereits ausgeschieden ist, Wurf ignorieren
    if p in game.finished_players:
        game.finish_dart()
        return

    # SCHRITT 2: Interaktion je nach Variante

    # 2.1 VARIANTE: STANDARD
    if game.killer_variante == "Standard":
        if not game.killer_status[p]:
            # Aufbauphase: Eigene Zahl treffen, um Leben zu sammeln
            if val == game.killer_numbers[p]:
                schaden = 2 if daten["was_double"] else 3 if daten["was_triple"] else 1

                if game.double_in:
                    # Double-In: Erst wenn das eigene Double getroffen wurde, dürfen Leben gesammelt werden
                    if not game.double_in_done[p]:
                        if daten["was_double"]:
                            game.double_in_done[p] = True
                            game.scores[p] = min(3, game.scores[p] + 2)
                    else:
                        game.scores[p] = min(3, game.scores[p] + schaden)
                else:
                    game.scores[p] = min(3, game.scores[p] + schaden)

                # Bei Erreichen von exakt 3 Leben wird der Spieler zum Killer
                if game.scores[p] == 3:
                    game.killer_status[p] = True
        else:
            # Jagdphase: Gegner angreifen
            if val in game.killer_numbers and val != game.killer_numbers[p]:
                g_idx = game.killer_numbers.index(val)
                if g_idx not in game.finished_players:
                    schaden = (
                        2 if daten["was_double"] else 3 if daten["was_triple"] else 1
                    )

                    # Double-Out Prüfung (Todesstoß nur auf Double oder Triple)
                    potential_new_lives = game.scores[g_idx] - schaden
                    if potential_new_lives <= 0 and game.double_out:
                        if not daten["was_double"] and not daten["was_triple"]:
                            # Einfacher Treffer zieht Leben ab, kann aber nicht eliminieren (Gegner bleibt bei 1 Leben)
                            schaden = game.scores[g_idx] - 1

                    game.scores[g_idx] = max(0, game.scores[g_idx] - schaden)
                    if game.scores[g_idx] == 0:
                        game.finished_players.append(g_idx)

    # 2.2 VARIANTE: DIREKT-KILLER
    elif game.killer_variante == "Direkt-Killer":
        # Aktivierungsprüfung für Double-In (Killer freischalten)
        if game.double_in and not game.killer_status[p]:
            if val == game.killer_numbers[p] and daten["was_double"]:
                game.killer_status[p] = True
        else:
            # Eigene Fehler: Double/Triple auf eigene Nummer zieht 1 Leben ab
            if val == game.killer_numbers[p]:
                if daten["was_double"] or daten["was_triple"]:
                    game.scores[p] = max(0, game.scores[p] - 1)
                    if game.scores[p] == 0:
                        game.finished_players.append(p)
            # Gegner angreifen
            elif val in game.killer_numbers:
                g_idx = game.killer_numbers.index(val)
                if g_idx not in game.finished_players:
                    schaden = (
                        2 if daten["was_double"] else 3 if daten["was_triple"] else 1
                    )

                    # Double-Out Prüfung
                    potential_new_lives = game.scores[g_idx] - schaden
                    if potential_new_lives <= 0 and game.double_out:
                        if not daten["was_double"] and not daten["was_triple"]:
                            schaden = game.scores[g_idx] - 1

                    game.scores[g_idx] = max(0, game.scores[g_idx] - schaden)
                    if game.scores[g_idx] == 0:
                        game.finished_players.append(g_idx)

    # 2.3 VARIANTE: TOTALER KRIEG
    elif game.killer_variante == "Totaler Krieg":
        # Eigene Fehler: Double = -2 Leben, Triple = -3 Leben (Selbstelimination)
        if val == game.killer_numbers[p]:
            if daten["was_double"]:
                game.scores[p] = max(0, game.scores[p] - 2)
            elif daten["was_triple"]:
                game.scores[p] = max(0, game.scores[p] - 3)

            if game.scores[p] == 0:
                game.finished_players.append(p)
        # Gegner angreifen
        elif val in game.killer_numbers:
            g_idx = game.killer_numbers.index(val)
            if g_idx not in game.finished_players:
                if daten["was_triple"]:
                    # One-Shot-Kill: Sofortige Elimination
                    game.scores[g_idx] = 0
                    game.finished_players.append(g_idx)
                elif daten["was_double"]:
                    # Double zieht 2 Leben ab
                    game.scores[g_idx] = max(0, game.scores[g_idx] - 2)
                    if game.scores[g_idx] == 0:
                        game.finished_players.append(g_idx)
                else:
                    # Single zieht standardmäßig 1 Leben ab
                    game.scores[g_idx] = max(0, game.scores[g_idx] - 1)
                    if game.scores[g_idx] == 0:
                        game.finished_players.append(g_idx)

    # SCHRITT 3: Siegbedingung prüfen (Wer als letztes übrig bleibt, gewinnt)
    lebende_spieler = [
        i for i in range(len(game.players)) if i not in game.finished_players
    ]
    if len(lebende_spieler) == 1:
        gewinner = lebende_spieler[0]
        if gewinner not in game.finished_players:
            game.finished_players.insert(0, gewinner)  # Setzt den Gewinner auf Platz 1
        game.wait_and_next_player()
        return

    game.finish_dart()
