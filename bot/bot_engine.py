import random
from dart_cup import SPIEL_MODI
try:
    from bot import bot_classic
except ImportError:
    import bot_classic

def calculate_human_average(match_log, player_map):
    human_throws = [log for log in match_log if player_map.get(log["spieler"], "Mensch") == "Mensch"]
    if not human_throws:
        return 66.0
    total_points = sum(log["wert"] * log["multiplikator"] for log in human_throws)
    total_darts = len(human_throws)
    return (total_points / total_darts) * 3 if total_darts > 0 else 40.0

def get_bot_throw(game_mode, current_score, bot_type, match_log=[], player_map={}, double_in=False, double_out=False):
    if bot_type.lower() == "dynamisch":
        avg = calculate_human_average(match_log, player_map)
        if avg < 25: level = 1
        elif avg < 35: level = 2
        elif avg < 42: level = 3
        elif avg < 50: level = 4
        elif avg < 58: level = 5
        elif avg < 65: level = 6
        elif avg < 75: level = 7
        elif avg < 85: level = 8
        elif avg < 95: level = 9
        else: level = 10
    else:
        try:
            level = int(bot_type.split()[-1])
        except:
            level = 1

    is_x01_type = True
    current_mode_key = None
    for mode_name in SPIEL_MODI:
        core_name = mode_name.split()[0]
        if core_name in game_mode:
            current_mode_key = mode_name
            if len(SPIEL_MODI[mode_name]) > 3:
                is_x01_type = SPIEL_MODI[mode_name][3]
            break

    if is_x01_type:
        # Hier werden double_in und double_out an bot_classic durchgereicht
        return bot_classic.get_throw(current_score, level, double_in, double_out)

    elif current_mode_key == "Cricket":
        pass
    elif "Clock" in current_mode_key:
        pass

    return (random.randint(1, 20), 1)
