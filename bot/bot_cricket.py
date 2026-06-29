# bot/bot_cricket.py
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
    if game is None or not hasattr(game, "cricket_stat"):
        # Fallback, falls kein Spiel-Zustand ausgelesen werden konnte
        target_num = 20
        target_mult = 3 if level >= 5 else 1
    else:
        p = game.current_player_idx
        variante = getattr(game, "cricket_variante", "Standard")
        cricket_stat = game.cricket_stat
        scores = game.scores
        players_count = len(game.players)

        # Hilfsfunktion: Kann der Bot auf diesem Feld aktuell punkten?
        def can_score_on(num):
            if cricket_stat[p].get(num, 0) < 3:
                return False
            # Mindestens ein Gegner hat das Feld noch offen
            return any(
                cricket_stat[i].get(num, 0) < 3 for i in range(players_count) if i != p
            )

        numbers = [20, 19, 18, 17, 16, 15, 25]
        target_num = None

        # 1. TAKTIK: NO-SCORE (Wer zuerst alles zu hat, gewinnt sofort)
        if variante == "No-Score":
            # Bot wirft einfach auf das höchste noch offene eigene Segment
            for num in numbers:
                if cricket_stat[p].get(num, 0) < 3:
                    target_num = num
                    break
            if target_num is None:
                target_num = 25

        # 2. TAKTIK: CUT-THROAT (Punkte sind Strafpunkte, niedrigster Score gewinnt)
        elif variante == "Cut-Throat":
            highest_open = None
            for num in numbers:
                if cricket_stat[p].get(num, 0) < 3:
                    highest_open = num
                    break

            score_targets = [num for num in numbers if can_score_on(num)]
            my_score = scores[p]
            max_score = max(scores)

            # Wenn wir die meisten Punkte haben (verlieren), versuchen wir, den anderen Punkte aufzudrücken
            if my_score == max_score and score_targets:
                target_num = score_targets[
                    0
                ]  # Höchstes Punkte-Feld, um Gegner zu bestrafen
            else:
                target_num = highest_open  # Ansonsten primär eigene Felder schließen

            if target_num is None:
                target_num = 25

        # 3. TAKTIK: STANDARD CRICKET (Punkte sind gut, höchster Score gewinnt)
        else:
            my_score = scores[p]
            opponents_scores = [scores[i] for i in range(players_count) if i != p]
            max_opponent_score = max(opponents_scores) if opponents_scores else 0
            score_targets = [num for num in numbers if can_score_on(num)]

            # Wenn wir punktetechnisch hinten liegen, versuchen wir primär zu punkten
            if my_score < max_opponent_score and score_targets:
                target_num = score_targets[0]
            else:
                # Ansonsten schließen wir das höchste noch offene Segment
                for num in numbers:
                    if cricket_stat[p].get(num, 0) < 3:
                        target_num = num
                        break

            if target_num is None:
                # Fallback: Wenn alles zu ist, aber wir noch Punkte brauchen
                if score_targets:
                    target_num = score_targets[0]
                else:
                    target_num = 25

        # Multiplikator-Auswahl basierend auf Level und Ziel
        if target_num == 25:
            target_mult = 2 if level >= 7 else 1  # Starke Bots zielen auf Double-Bull
        else:
            target_mult = 3 if level >= 5 else 1  # Ab Level 5 wird das Triple anvisiert

    # Koordinaten ermitteln
    target_r, target_angle = get_coordinates_for_target(target_num, target_mult)

    # Streuung (Sigma) berechnen
    if player_avg is not None and player_avg > 0:
        sigma = max(65.0 - (0.35 * player_avg), 5.0)
    else:
        sigma = 5.0 + (10.0 - level) ** 2 * 1.0

    if target_num == 25:
        sigma = sigma * 1.15  # Das Bullseye ist etwas schwerer zu fokussieren

    # Wurf ausführen
    target_x = target_r * math.cos(math.radians(target_angle))
    target_y = target_r * math.sin(math.radians(target_angle))
    final_x = random.gauss(target_x, sigma)
    final_y = random.gauss(target_y, sigma)
    final_r = math.sqrt(final_x**2 + final_y**2)
    final_angle = math.degrees(math.atan2(final_y, final_x))

    return get_score_from_polar(final_r, final_angle)
