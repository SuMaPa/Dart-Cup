import random
from dart_cup import SPIEL_MODI

# Imports für die KI-Funktionen
try:
    from bot import bot_classic
    from bot import bot_elimination
    from bot import bot_mensch
    from bot import bot_clock
except ImportError:
    import bot_classic
    import bot_elimination
    import bot_mensch
    import bot_clock

# Imports für die echten Spiellogik-Funktionen (für den direkten Abgleich)
try:
    from spiel import classic
    from spiel import elimination
    from spiel import mensch
    from spiel import clock
except ImportError:
    import classic
    import elimination
    import mensch
    import clock


def calculate_human_average(match_log, player_map):
    human_throws = [log for log in match_log if player_map.get(log["spieler"], "Mensch") == "Mensch"]

    if human_throws:
        player_stats = {}
        for log in human_throws:
            p_name = log["spieler"]
            if p_name not in player_stats:
                player_stats[p_name] = {"points": 0, "darts": 0}
            player_stats[p_name]["points"] += log["wert"] * log["multiplikator"]
            player_stats[p_name]["darts"] += 1

        averages = sorted([(stats["points"] / stats["darts"]) * 3 for stats in player_stats.values() if stats["darts"] > 0])
    else:
        bot_throws = [log for log in match_log if player_map.get(log["spieler"], "Mensch") != "Mensch" and log["spieler"] != "BotDynamisch"]
        if not bot_throws:
            return 45.0

        bot_stats = {}
        for log in bot_throws:
            bot_name = log["spieler"]
            if bot_name not in bot_stats:
                bot_stats[bot_name] = {"points": 0, "darts": 0}
            bot_stats[bot_name]["points"] += log["wert"] * log["multiplikator"]
            bot_stats[bot_name]["darts"] += 1

        averages = sorted([(stats["points"] / stats["darts"]) * 3 for stats in bot_stats.values() if stats["darts"] > 0])

    if not averages:
        return 45.0

    n = len(averages)
    if n % 2 == 1:
        return averages[n // 2]
    else:
        return (averages[n // 2 - 1] + averages[n // 2]) / 2

#def get_bot_throw(game_mode, current_score, bot_type, match_log=[], player_map={}, double_in=False, double_out=False):
def get_bot_throw(game_mode, current_score, bot_type, match_log=[], player_map={}, double_in=False, double_out=False, variante="Standard"):
    # Wir suchen die passende Prozess-Funktion aus SPIEL_MODI heraus
    aktuelle_prozess_fn = None
    for mode_name, mode_tuple in SPIEL_MODI.items():
        if mode_name in game_mode:
            aktuelle_prozess_fn = mode_tuple[0]  # Das erste Element ist die Prozess_Fn
            break

    if bot_type.lower() == "dynamisch":
        chosen_level = 5
        current_avg = calculate_human_average(match_log, player_map)
    else:
        current_avg = None
        try:
            chosen_level = int(bot_type.split()[-1])
        except:
            chosen_level = 1

    # Der geniale Abgleich direkt über die Funktionsobjekte statt wackeligem Text
    if aktuelle_prozess_fn:
        if aktuelle_prozess_fn == clock.process_around_the_clock:
            #return bot_clock.get_throw(current_target=current_score, level=chosen_level, player_avg=current_avg)
            return bot_clock.get_throw(current_target=current_score, level=chosen_level, variante=variante, player_avg=current_avg)
        elif aktuelle_prozess_fn == elimination.process_elimination:
            return bot_elimination.get_throw(current_score, chosen_level, double_in, double_out, player_avg=current_avg)

        elif aktuelle_prozess_fn == mensch.process_mensch:
            return bot_mensch.get_throw(current_score, chosen_level, double_in, double_out, player_avg=current_avg)

    # Fallback für Classic X01 (classic.process_classic) und alles andere
    return bot_classic.get_throw(current_score, chosen_level, double_in, double_out, player_avg=current_avg)
