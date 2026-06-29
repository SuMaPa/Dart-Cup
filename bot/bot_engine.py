# bot/bot_engine.py
import random
import re

# Saubere, direkte Imports der KI-Klassen
from bot import bot_classic
from bot import bot_elimination
from bot import bot_mensch
from bot import bot_clock
from bot import bot_cricket
from bot import bot_bob
from bot import bot_killer
from bot import bot_shanghai
from bot import bot_halve_it

# Saubere, direkte Imports der Spiellogiken
from spiel import classic
from spiel import elimination
from spiel import mensch
from spiel import clock
from spiel import cricket
from spiel import bob
from spiel import killer
from spiel import shanghai
from spiel import halve_it


def get_game_instance():
    """Nutzt Call-Stack-Inspektion, um das aktive UI-Objekt auszulesen."""
    import inspect

    frame = inspect.currentframe()
    while frame:
        if "self" in frame.f_locals:
            obj = frame.f_locals["self"]
            # Prüfen, ob das Objekt die Spiel-Eigenschaften besitzt
            if hasattr(obj, "players") and hasattr(obj, "current_player_idx"):
                return obj
        frame = frame.f_back
    return None


def calculate_human_average(match_log, player_map):
    human_throws = [
        log for log in match_log if player_map.get(log["spieler"], "Mensch") == "Mensch"
    ]

    if human_throws:
        player_stats = {}
        for log in human_throws:
            p_name = log["spieler"]
            if p_name not in player_stats:
                player_stats[p_name] = {"points": 0, "darts": 0}
            player_stats[p_name]["points"] += log["wert"] * log["multiplikator"]
            player_stats[p_name]["darts"] += 1

        averages = sorted(
            [
                (stats["points"] / stats["darts"]) * 3
                for stats in player_stats.values()
                if stats["darts"] > 0
            ]
        )
    else:
        bot_throws = [
            log
            for log in match_log
            if player_map.get(log["spieler"], "Mensch") != "Mensch"
        ]
        if bot_throws:
            player_stats = {}
            for log in bot_throws:
                p_name = log["spieler"]
                if p_name not in player_stats:
                    player_stats[p_name] = {"points": 0, "darts": 0}
                player_stats[p_name]["points"] += log["wert"] * log["multiplikator"]
                player_stats[p_name]["darts"] += 1
            averages = sorted(
                [
                    (stats["points"] / stats["darts"]) * 3
                    for stats in player_stats.values()
                    if stats["darts"] > 0
                ]
            )
        else:
            averages = [40.0]

    if averages:
        return sum(averages) / len(averages)
    return 40.0


def get_bot_throw(
    game_mode,
    current_score,
    bot_type,
    match_log,
    player_map,
    double_in=False,
    double_out=False,
    variante="Standard",
):
    from dart_cup import (
        SPIEL_MODI,
    )  # Lokaler Import bricht die zirkuläre Import-Kette auf!

    # Finde die passende Spiellogik aus SPIEL_MODI heraus
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

        # Mapping von Text-Schwierigkeitsgraden auf die internen Bot-Level (1 bis 10)
        difficulty_mapping = {"leicht": 2, "mittel": 5, "schwer": 8, "profi": 10}
        type_lower = bot_type.lower()
        chosen_level = 1  # Standard-Fallback

        # Prüfen, ob einer der Text-Schwierigkeitsgrade im String vorkommt
        for keyword, lvl in difficulty_mapping.items():
            if keyword in type_lower:
                chosen_level = lvl
                break
        else:
            # Fallback für numerische Angaben wie "Level 5" oder reine Ganzzahlen
            try:
                chosen_level = int(bot_type.split()[-1])
            except ValueError:
                try:
                    chosen_level = int(bot_type)
                except ValueError:
                    chosen_level = 1

    # Der geniale Abgleich direkt über die Funktionsobjekte statt wackeligem Text
    if aktuelle_prozess_fn:
        if aktuelle_prozess_fn == clock.process_around_the_clock:
            return bot_clock.get_throw(
                current_target=current_score,
                level=chosen_level,
                variante=variante,
                player_avg=current_avg,
            )
        elif aktuelle_prozess_fn == elimination.process_elimination:
            return bot_elimination.get_throw(
                current_score,
                chosen_level,
                double_in,
                double_out,
                player_avg=current_avg,
            )
        elif aktuelle_prozess_fn == mensch.process_mensch:
            return bot_mensch.get_throw(
                current_score,
                chosen_level,
                double_in,
                double_out,
                player_avg=current_avg,
            )
        elif aktuelle_prozess_fn == cricket.process_cricket:
            game = get_game_instance()
            return bot_cricket.get_throw(
                level=chosen_level, player_avg=current_avg, game=game
            )
        elif aktuelle_prozess_fn == bob.spiel_bobs27:
            game = get_game_instance()
            return bot_bob.get_throw(
                level=chosen_level, player_avg=current_avg, game=game
            )
        elif aktuelle_prozess_fn == killer.process_killer:
            game = get_game_instance()
            return bot_killer.get_throw(
                level=chosen_level, player_avg=current_avg, game=game
            )
        elif aktuelle_prozess_fn == shanghai.process_shanghai:
            game = get_game_instance()
            return bot_shanghai.get_throw(
                level=chosen_level, player_avg=current_avg, game=game
            )
        elif aktuelle_prozess_fn == halve_it.process_halve_it:
            game = get_game_instance()
            return bot_halve_it.get_throw(
                level=chosen_level, player_avg=current_avg, game=game
            )
        else:
            return bot_classic.get_throw(
                current_score,
                chosen_level,
                double_in,
                double_out,
                player_avg=current_avg,
            )

    return bot_classic.get_throw(
        current_score, chosen_level, double_in, double_out, player_avg=current_avg
    )
