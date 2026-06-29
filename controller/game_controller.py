# controller/game_controller.py
import random
from PyQt6.QtCore import QTimer
from logs.stats_manager import save_match_stats


class GameController:
    def __init__(self, ui):
        self.ui = ui

    def start_game(self):
        from dart_cup import SPIEL_MODI

        temp_map = {}
        for i, inp in enumerate(self.ui.player_inputs):
            name = inp.text().strip()
            if name and i < len(self.ui.bot_types):
                temp_map[name] = self.ui.bot_types[i].currentText()

        self.ui.save_settings()
        names = [
            inp.text().strip() for inp in self.ui.player_inputs if inp.text().strip()
        ]
        if not names:
            names = ["Spieler 1"]
            temp_map["Spieler 1"] = "Mensch"

        if self.ui.cb_randomize.isChecked():
            random.shuffle(names)

        self.ui.players = names[:8]
        self.ui.player_map = {
            name: temp_map.get(name, "Mensch") for name in self.ui.players
        }

        haupt_modus = self.ui.mode_box.currentText()
        variante = self.ui.variant_box.currentText()
        hat_varianten = False
        is_x01_type = True
        if haupt_modus in SPIEL_MODI:
            hat_varianten = SPIEL_MODI[haupt_modus][2] is not None
            if len(SPIEL_MODI[haupt_modus]) > 3:
                is_x01_type = SPIEL_MODI[haupt_modus][3]
        if hat_varianten:
            basis_modus = haupt_modus.replace(" X01", "")
            self.ui.game_mode = f"{basis_modus} {variante}"
        else:
            self.ui.game_mode = haupt_modus

        self.ui.limit = 301
        if haupt_modus in SPIEL_MODI:
            SPIEL_MODI[haupt_modus][1](self.ui)

        self.ui.start_score_val = self.ui.scores[0]
        self.ui.is_bust = [False] * len(self.ui.players)
        if is_x01_type:
            self.ui.has_entered = [not self.ui.cb_double_in.isChecked()] * len(
                self.ui.players
            )
        else:
            self.ui.has_entered = [True] * len(self.ui.players)
        self.ui.last_darts = [[] for _ in range(len(self.ui.players))]
        self.ui.finished_players = []
        self.ui.double_out = self.ui.cb_double_out.isChecked() if is_x01_type else False
        self.ui.current_player_idx = 0
        self.ui.current_round = 1
        self.ui.is_x01_type = is_x01_type  # NEU: Spieltyp für spätere Prüfungen sichern
        self.ui.darts_thrown = 0
        self.ui.history = []
        self.ui.modifier = 1
        self.ui.typed_score = ""
        self.ui.score_at_start_of_turn = self.ui.scores[0]
        self.ui.table.setRowCount(len(self.ui.players))
        self.ui.set_buttons_enabled(True)
        self.ui.match_log = []
        self.ui.load_live_ui()
        if hasattr(self.ui, "undo_btn"):
            self.ui.undo_btn.setVisible(True)
        if hasattr(self.ui, "nochmal_btn"):
            self.ui.nochmal_btn.setVisible(False)
        self.ui.back_btn.setText("Abbrechen")
        self.ui.back_btn.setStyleSheet("background-color: #454a4f; height: 35px;")
        self.ui.update_display()
        QTimer.singleShot(1, self.ui.switch_to_game_window)

        first_player = self.ui.players[0]
        if self.ui.player_map.get(first_player, "Mensch") != "Mensch":
            self.ui.set_buttons_enabled(False)
            self.ui.bot_timer.start(1500)

    def num_clicked(self, val):
        from dart_cup import SPIEL_MODI

        if self.ui.darts_thrown == 0:
            self.ui.busted_before_turn = list(self.ui.is_bust)

        if not hasattr(self.ui, "current_turn_kill"):
            self.ui.current_turn_kill = False

        state = (
            list(self.ui.scores),
            list(self.ui.has_entered),
            self.ui.current_player_idx,
            self.ui.darts_thrown,
            self.ui.score_at_start_of_turn,
            [list(d) for d in self.ui.last_darts],
            list(self.ui.is_bust),
            list(self.ui.finished_players),
            list(self.ui.match_log),
            self.ui.current_turn_kill,
            self.ui.current_round,
        )
        self.ui.history.append(state)

        haupt_modus = self.ui.mode_box.currentText()
        is_x01_type = True
        if haupt_modus in SPIEL_MODI and len(SPIEL_MODI[haupt_modus]) > 3:
            is_x01_type = SPIEL_MODI[haupt_modus][3]
        if self.ui.darts_thrown == 0:
            if is_x01_type:
                self.ui.is_bust[self.ui.current_player_idx] = False
            self.ui.last_darts[self.ui.current_player_idx] = []

        if val == 0 or self.ui.modifier == "Miss":
            val = 0
            self.ui.modifier = 1
            dart_str = "Miss"
        else:
            if val == 25 and self.ui.modifier == 3:
                self.ui.modifier = 1
            prefix = (
                "D" if self.ui.modifier == 2 else "T" if self.ui.modifier == 3 else ""
            )
            dart_str = (
                f"{prefix}{val}"
                if val != 25
                else ("BULL" if self.ui.modifier == 1 else "D-BULL")
            )

        points = val * self.ui.modifier
        was_double = self.ui.modifier == 2
        self.ui.last_darts[self.ui.current_player_idx].append(dart_str)

        daten = {
            "val": val,
            "points": points,
            "was_double": was_double,
            "was_triple": (self.ui.modifier == 3),
        }
        self.ui.match_log.append(
            {
                "spieler": self.ui.players[self.ui.current_player_idx],
                "wurf": dart_str,
                "wert": val,
                "multiplikator": self.ui.modifier,
            }
        )

        modus_daten = SPIEL_MODI.get(haupt_modus)
        if modus_daten:
            modus_daten[0](self.ui, daten)

        busted_before = getattr(
            self.ui, "busted_before_turn", [False] * len(self.ui.players)
        )
        for i in range(len(self.ui.players)):
            if self.ui.is_bust[i] and not busted_before[i]:
                self.ui.current_turn_kill = True

        self.ui.btn_double.setChecked(False)
        self.ui.btn_triple.setChecked(False)
        self.ui.modifier = 1
        self.ui.typed_score = ""

    def next_player(self):
        is_x01_type = getattr(self.ui, "is_x01_type", True)

        # Spielende-Bedingung berechnen
        if not is_x01_type:
            # Runden- / Highscore-Spiele (Halve It, Shanghai, Bob's 27):
            # Diese enden grundsätzlich erst, wenn ALLE Spieler fertiggespielt haben!
            game_over = len(self.ui.finished_players) >= len(self.ui.players)
        else:
            # Klassische X01-Spiele:
            if self.ui.cb_play_to_end.isChecked():
                game_over = len(self.ui.finished_players) >= len(
                    self.ui.players
                ) - 1 or (
                    len(self.ui.players) == 1 and len(self.ui.finished_players) == 1
                )
            else:
                game_over = len(self.ui.finished_players) > 0

        if game_over:
            self.ui.bot_timer.stop()
            self.ui.turn_timer.stop()

            if self.ui.cb_play_to_end.isChecked():
                for i in range(len(self.ui.players)):
                    if i not in self.ui.finished_players:
                        self.ui.finished_players.append(i)

            save_match_stats(
                self.ui.game_mode,
                self.ui.finished_players,
                self.ui.players,
                self.ui.match_log,
            )

            self.ui.score_label.setText("FINISH!")
            self.ui.score_label.setStyleSheet(
                "font-size: 80px; font-weight: bold; color: #27ae60;"
            )

            if hasattr(self.ui, "info_label"):
                self.ui.info_label.setText("Spiel beendet")
            if hasattr(self.ui, "undo_btn"):
                self.ui.undo_btn.setVisible(False)
            if hasattr(self.ui, "nochmal_btn"):
                self.ui.nochmal_btn.setVisible(True)
            self.ui.back_btn.setEnabled(True)
            self.ui.back_btn.setVisible(True)
            self.ui.back_btn.setText("Beenden")
            self.ui.back_btn.setStyleSheet(
                "background-color: #27ae60; color: black; font-weight: bold; height: 35px;"
            )
            self.ui.set_buttons_enabled(False)
            return

        self.ui.darts_thrown = 0
        self.ui.current_turn_kill = False

        prev_idx = self.ui.current_player_idx

        while True:
            self.ui.current_player_idx = (self.ui.current_player_idx + 1) % len(
                self.ui.players
            )
            if self.ui.current_player_idx not in self.ui.finished_players:
                break

        if self.ui.current_player_idx <= prev_idx:
            self.ui.current_round += 1

        self.ui.is_bust[self.ui.current_player_idx] = False
        self.ui.score_at_start_of_turn = self.ui.scores[self.ui.current_player_idx]
        self.ui.update_display()

        current_name = self.ui.players[self.ui.current_player_idx]
        if self.ui.player_map.get(current_name, "Mensch") != "Mensch":
            self.ui.set_buttons_enabled(False)
            self.ui.bot_timer.start(1500)
        else:
            self.ui.set_buttons_enabled(True)

    def undo_hit(self):
        if not self.ui.history:
            return
        self.ui.turn_timer.stop()
        self.ui.bot_timer.stop()
        state = self.ui.history.pop()
        (
            self.ui.scores,
            self.ui.has_entered,
            self.ui.current_player_idx,
            self.ui.darts_thrown,
            self.ui.score_at_start_of_turn,
            self.ui.last_darts,
            self.ui.is_bust,
            self.ui.finished_players,
            self.ui.match_log,
            self.ui.current_turn_kill,
            self.ui.current_round,
        ) = state

        current_name = self.ui.players[self.ui.current_player_idx]
        if self.ui.player_map.get(current_name, "Mensch") != "Mensch":
            self.ui.set_buttons_enabled(False)
            self.ui.bot_timer.start(1500)
        else:
            self.ui.set_buttons_enabled(True)
        self.ui.update_display()
