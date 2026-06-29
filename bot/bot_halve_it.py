# bot/bot_halve_it.py
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
    if game is None or not hasattr(game, "scores"):
        target_num, target_mult = 20, 1
    else:
        p = game.current_player_idx
        aktuelle_runde = getattr(game, "current_round", 1) - 1
        targets = getattr(game, "halve_it_targets", [])

        if aktuelle_runde >= len(targets):
            target_num, target_mult = 20, 1
        else:
            ziel = targets[aktuelle_runde]

            if ziel == "SCORING":
                target_num, target_mult = 20, 3  # Triple 20 für maximale Ausbeute
            elif ziel == "DOUBLE":
                target_num, target_mult = 20, 2  # D20
            elif ziel == "TRIPLE":
                target_num, target_mult = 20, 3  # T20
            elif ziel == "BULL":
                target_num, target_mult = 25, 2 if level >= 7 else 1
            elif ziel == "BULLSEYE":
                target_num, target_mult = 25, 2
            elif ziel == "ROT":
                target_num, target_mult = (
                    20,
                    3,
                )  # T20 ist rot eingedeckt und bringt 60 Punkte
            elif ziel == "T20":
                target_num, target_mult = 20, 3
            elif ziel == "D20":
                target_num, target_mult = 20, 2
            elif ziel == "3_FARBEN":
                # Der Bot wechselt seine Wurf-Ziele taktisch, um 3 Farben zu treffen
                darts_thrown = getattr(game, "darts_thrown", 0)
                if darts_thrown == 0:
                    target_num, target_mult = 20, 3  # Red (T20)
                elif darts_thrown == 1:
                    target_num, target_mult = 20, 1  # Black (S20)
                else:
                    target_num, target_mult = 1, 1  # White (S1)
            elif ziel.isdigit():
                target_num = int(ziel)
                target_mult = 3 if level >= 5 else 1
            else:
                target_num, target_mult = 20, 1

    # Koordinaten berechnen
    target_r, target_angle = get_coordinates_for_target(target_num, target_mult)

    # Streuung (Sigma) berechnen
    if player_avg is not None and player_avg > 0:
        sigma = max(65.0 - (0.35 * player_avg), 5.0)
    else:
        sigma = 5.0 + (10.0 - level) ** 2 * 1.0

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
