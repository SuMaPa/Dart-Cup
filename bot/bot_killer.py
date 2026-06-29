# bot/bot_killer.py
import random
import math

BULLSEYE_RADIUS = 6.35
BULL_RADIUS = 15.9
INNER_TREBLE = 97.0
OUTER_TREBLE = 107.0
INNER_DOUBLE = 160.0
OUTER_DOUBLE = 170.0
BOARD_RADIUS = 170.0
SEGMENTS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
SEGMENT_ANGLE = 18.0
HALF_SEGMENT = 9.0


def get_coordinates_for_target(number, multiplier):
    if number == 25:
        if multiplier == 2:
            return 0.0, 0.0
        else:
            return (BULLSEYE_RADIUS + BULL_RADIUS) / 2, 0.0
    try:
        idx = SEGMENTS.index(number)
    except ValueError:
        idx = 0
    angle = 90.0 - (idx * SEGMENT_ANGLE)
    if multiplier == 3:
        r = (INNER_TREBLE + OUTER_TREBLE) / 2
    elif multiplier == 2:
        r = (INNER_DOUBLE + OUTER_DOUBLE) / 2
    else:
        r = (BULL_RADIUS + INNER_TREBLE) / 2
    return r, angle


def get_score_from_polar(r, angle):
    if r > BOARD_RADIUS:
        return (0, 1)
    if r <= BULLSEYE_RADIUS:
        return (25, 2)
    if r <= BULL_RADIUS:
        return (25, 1)
    angle = angle % 360
    shifted_angle = (90 - angle + HALF_SEGMENT) % 360
    idx = int(shifted_angle // SEGMENT_ANGLE) % 20
    number = SEGMENTS[idx]
    if INNER_TREBLE <= r <= OUTER_TREBLE:
        return (number, 3)
    elif INNER_DOUBLE <= r <= OUTER_DOUBLE:
        return (number, 2)
    else:
        return (number, 1)


def get_throw(level, player_avg=None, game=None):
    if game is None or not hasattr(game, "killer_numbers"):
        # Fallback falls kein Spiel-Zustand auslesbar ist
        target_num = 20
        target_mult = 1
    else:
        p = game.current_player_idx
        my_num = game.killer_numbers[p]
        is_killer = game.killer_status[p]
        variante = getattr(game, "killer_variante", "Standard")
        double_in = getattr(game, "double_in", False)
        double_in_done = (
            game.double_in_done[p] if hasattr(game, "double_in_done") else True
        )

        # SCHRITT 1: Eigene Nummer wählen (für alle Varianten gleich)
        if my_num == 0:
            # Finde die höchste freie Zahl ab 20 abwärts (Bullseye ist verboten)
            chosen_target = 20
            for num in [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10]:
                if num not in game.killer_numbers:
                    chosen_target = num
                    break
            target_num = chosen_target
            target_mult = 1  # Sicher das Single-Feld werfen, um zu registrieren
        else:
            # Hilfsfunktion: Finde den stärksten Gegner im Spiel, der noch lebt
            def find_best_opponent():
                best_g = None
                max_lives = -1
                for g in range(len(game.players)):
                    if (
                        g != p
                        and g not in game.finished_players
                        and game.scores[g] > max_lives
                    ):
                        if game.killer_numbers[g] > 0:
                            max_lives = game.scores[g]
                            best_g = g
                return best_g

            # SCHRITT 2: Taktik basierend auf Variante
            if variante == "Standard":
                if not is_killer:
                    # PRIORITÄT 1: Eigene Leben füllen!
                    target_num = my_num
                    if double_in and not double_in_done:
                        target_mult = 2  # Double In zwingend nötig zum Freischalten
                    else:
                        # Triple oder Double anvisieren, um schneller auf 3 Leben zu kommen
                        target_mult = 3 if level >= 5 else 1
                else:
                    # Wir sind Killer -> Gegner jagen!
                    g_idx = find_best_opponent()
                    if g_idx is not None:
                        target_num = game.killer_numbers[g_idx]
                        target_mult = 3 if level >= 7 else (2 if level >= 4 else 1)
                    else:
                        # Fallback falls kein Gegner aktiv/lebendig
                        target_num = my_num
                        target_mult = 1

            elif variante == "Direkt-Killer":
                # Aktivierungsprüfung für Double-In (Gesperrt bis Double geworfen)
                if double_in and not is_killer:
                    target_num = my_num
                    target_mult = 2
                else:
                    # Sofortige Jagd auf Gegner
                    g_idx = find_best_opponent()
                    if g_idx is not None:
                        target_num = game.killer_numbers[g_idx]
                        target_mult = 3 if level >= 7 else (2 if level >= 4 else 1)
                    else:
                        target_num = my_num
                        target_mult = 1

            elif variante == "Totaler Krieg":
                # Aggressive Jagd auf Triple für One-Shot-Kills
                g_idx = find_best_opponent()
                if g_idx is not None:
                    target_num = game.killer_numbers[g_idx]
                    target_mult = (
                        3 if level >= 6 else 2
                    )  # Hohe Priorität auf das Triple
                else:
                    target_num = my_num
                    target_mult = 1

    # Koordinaten ermitteln
    target_r, target_angle = get_coordinates_for_target(target_num, target_mult)

    # Streuung (Sigma) berechnen
    if player_avg is not None and player_avg > 0:
        sigma = max(65.0 - (0.35 * player_avg), 5.0)
    else:
        sigma = 5.0 + (10.0 - level) ** 2 * 1.0

    # Feinabstimmung der Genauigkeit
    if target_mult in [2, 3] and level >= 6:
        sigma = sigma * 0.9

    # Wurf ausführen
    target_x = target_r * math.cos(math.radians(target_angle))
    target_y = target_r * math.sin(math.radians(target_angle))
    final_x = random.gauss(target_x, sigma)
    final_y = random.gauss(target_y, sigma)
    final_r = math.sqrt(final_x**2 + final_y**2)
    final_angle = math.degrees(math.atan2(final_y, final_x))

    return get_score_from_polar(final_r, final_angle)
