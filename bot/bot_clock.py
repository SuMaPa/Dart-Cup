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
        # Bullseye (Double) oder Outer Bull (Single)
        return (0.0, 0.0) if multiplier == 2 else ((BULLSEYE_RADIUS + BULL_RADIUS) / 2, 0.0)
    try:
        idx = SEGMENTS.index(number)
    except ValueError:
        idx = 0
    angle = 90.0 - (idx * SEGMENT_ANGLE)
    # Zielradien für die Segmente
    if multiplier == 3:
        r = (INNER_TREBLE + OUTER_TREBLE) / 2
    elif multiplier == 2:
        r = (INNER_DOUBLE + OUTER_DOUBLE) / 2
    else:
        r = (BULL_RADIUS + INNER_TREBLE) / 2
    return r, angle

def get_score_from_polar(r, angle):
    if r > BOARD_RADIUS: return (0, 1)
    if r <= BULLSEYE_RADIUS: return (25, 2)
    if r <= BULL_RADIUS: return (25, 1)
    angle = angle % 360
    shifted_angle = (90 - angle + HALF_SEGMENT) % 360
    idx = int(shifted_angle // SEGMENT_ANGLE) % 20
    number = SEGMENTS[idx]
    if INNER_TREBLE <= r <= OUTER_TREBLE: return (number, 3)
    elif INNER_DOUBLE <= r <= OUTER_DOUBLE: return (number, 2)
    else: return (number, 1)

def get_throw(current_target, level, variante="Standard", player_avg=None):

    if player_avg is not None and player_avg > 0:
        sigma = max(50.0 - (0.5 * player_avg), 0.5)
    else:
        sigma = 120.0 if level == 1 else (0.1 + ((10 - level) ** 2.5) * 0.4)

    # Zielvorgabe: Hier wird jetzt strikt nach Variante unterschieden[cite: 8]
    if current_target == 25:
        target_num, target_mult = 25, 2 # Bullseye-Ziel[cite: 8]
    else:
        if variante == "Double-Only":
            target_num, target_mult = current_target, 2 # Double Ring[cite: 8]
        elif variante == "All-In":
            target_num, target_mult = current_target, 3 # Triple Ring[cite: 8]
        else:
            target_num, target_mult = current_target, 1 # Single Segment[cite: 8]

    target_r, target_angle = get_coordinates_for_target(target_num, target_mult)

    target_x = target_r * math.cos(math.radians(target_angle))
    target_y = target_r * math.sin(math.radians(target_angle))

    final_x = random.gauss(target_x, sigma)
    final_y = random.gauss(target_y, sigma)

    final_r = math.sqrt(final_x**2 + final_y**2)
    final_angle = math.degrees(math.atan2(final_y, final_x))
    return get_score_from_polar(final_r, final_angle)
