def init_around_the_clock(game):
    game.scores = [1] * len(game.players)
    # Variante aus UI auslesen
    variante = (
        game.variant_box.currentText() if hasattr(game, "variant_box") else "Standard"
    )
    game.clock_variante = (
        variante if variante in ["Standard", "Double-Only", "All-In"] else "Standard"
    )


def process_around_the_clock(game, daten):
    val = daten["val"]
    p = game.current_player_idx
    target = game.scores[p]

    is_hit = False
    schritte = 0  # Start mit 0

    if game.clock_variante == "Standard":
        if val == target:
            is_hit = True
            schritte = 1

    elif game.clock_variante == "Double-Only":
        # Hier MUSS es ein Double der Zielzahl sein
        if val == target and daten["was_double"]:
            is_hit = True
            schritte = 1

    elif game.clock_variante == "All-In":
        # Trifft er die Zielzahl?
        if val == target:
            is_hit = True
            # Logik: Single=1, Double=2, Triple=3
            if daten["was_triple"]:
                schritte = 3
            elif daten["was_double"]:
                schritte = 2
            else:
                schritte = 1

    if is_hit:
        neuer_score = target + schritte
        # Begrenzung auf 20
        if neuer_score > 20:
            game.scores[p] = 25
        else:
            game.scores[p] = neuer_score

    # Check auf Bullseye (25)
    if game.scores[p] == 25:
        # Hier prüfen wir: Ist 25 das Ziel?
        # Wenn der Treffer-Check oben auf 25 landete, muss jetzt die 25 getroffen werden
        if val == 25:
            game.scores[p] = 0
            game.finished_players.append(p)
            game.wait_and_next_player()
            return

    game.finish_dart()
