# logs/stats_manager.py
import os
import json
import datetime
from logs.log import logger

UI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.join(UI_DIR, "ui", "dart_settings.json")


def load_settings_data():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Settings: {e}")
    return {}


def save_settings_data(data):
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Settings: {e}")


def save_match_stats(game_mode, finished_players, players, match_log):
    try:
        platzierungen = {}
        for idx, p_idx in enumerate(finished_players):
            platzierungen[players[p_idx]] = idx + 1
        for idx, spieler_name in enumerate(players):
            if spieler_name not in platzierungen:
                platzierungen[spieler_name] = -1

        match_data = {
            "datum": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modus": game_mode,
            "gewinner": (
                players[finished_players[0]] if finished_players else players[0]
            ),
            "platzierungen": platzierungen,
            "teilnehmer": players,
            "verlauf": match_log,
        }
        os.makedirs("stats", exist_ok=True)
        dateiname = (
            f"stats/match_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(dateiname, "w", encoding="utf-8") as f:
            json.dump(match_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Statistik: {e}", exc_info=True)
