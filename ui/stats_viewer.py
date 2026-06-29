import os
import json


class DartStatsEngine:
    def __init__(self, stats_dir="stats"):
        self.stats_dir = stats_dir

    def load_all_matches(self):
        if not os.path.exists(self.stats_dir):
            return []
        files = [f for f in os.listdir(self.stats_dir) if f.endswith(".json")]
        matches = []
        for file in files:
            try:
                with open(
                    os.path.join(self.stats_dir, file), "r", encoding="utf-8"
                ) as f:
                    matches.append(json.load(f))
            except Exception as e:
                print(f"Fehler beim Laden der Datei {file}: {e}")
        matches.sort(key=lambda x: x.get("datum", ""), reverse=True)
        return matches

    def get_all_tracked_players(self):
        matches = self.load_all_matches()
        players = set()
        for m in matches:
            players.update(m.get("teilnehmer", []))

        return sorted(list(players))

    def calculate_player_profile(self, player_name):
        matches = self.load_all_matches()
        profile = {
            "matches_played": 0,
            "wins": 0,
            "win_rate": 0.0,
            "total_darts": 0,
            "x01_avg": 0.0,
            "180s": 0,
            "140s": 0,
            "100s": 0,
            "top_segments": [],
        }
        x01_points = 0
        x01_darts = 0
        segment_heatmap = {}
        for m in matches:
            if player_name not in m.get("teilnehmer", []):
                continue
            profile["matches_played"] += 1
            platzierungen = m.get("platzierungen", {})
            ist_gewinner = (
                (m.get("gewinner") == player_name)
                or (platzierungen.get(player_name) == 1)
                or (platzierungen.get("Platz 1") == player_name)
            )
            if ist_gewinner:
                profile["wins"] += 1
            is_x01 = "Classic" in m.get("modus", "") or "X01" in m.get("modus", "")
            spieler_wuerfe = [
                w for w in m.get("verlauf", []) if w.get("spieler") == player_name
            ]
            current_turn_score = 0
            darts_in_turn = 0
            for wurf in spieler_wuerfe:
                profile["total_darts"] += 1
                val_str = wurf.get("wurf", "0")
                punkte = wurf.get("wert", 0) * wurf.get("multiplikator", 1)
                segment_heatmap[val_str] = segment_heatmap.get(val_str, 0) + 1
                if is_x01:
                    x01_points += punkte
                    x01_darts += 1
                    current_turn_score += punkte
                    darts_in_turn += 1
                    if darts_in_turn == 3:
                        if current_turn_score == 180:
                            profile["180s"] += 1
                        elif current_turn_score >= 140:
                            profile["140s"] += 1
                        elif current_turn_score >= 100:
                            profile["100s"] += 1
                        current_turn_score = 0
                        darts_in_turn = 0
            if darts_in_turn > 0 and is_x01:
                if current_turn_score == 180:
                    profile["180s"] += 1
                elif current_turn_score >= 140:
                    profile["140s"] += 1
                elif current_turn_score >= 100:
                    profile["100s"] += 1
        if profile["matches_played"] > 0:
            profile["win_rate"] = (profile["wins"] / profile["matches_played"]) * 100
        if x01_darts > 0:
            profile["x01_avg"] = (x01_points / x01_darts) * 3
        sorted_segments = sorted(
            segment_heatmap.items(), key=lambda x: x[1], reverse=True
        )
        profile["top_segments"] = sorted_segments[:3]
        return profile
