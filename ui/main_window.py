import random, json, os, datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QGraphicsOpacityEffect, QTableWidgetItem, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QColor, QKeyEvent
from ui.styles import MAIN_STYLE
from ui.setup_view import create_setup_ui
from ui.game_view import create_game_ui
from ui.stats_view import StatsWindow
from dart_cup import SPIEL_MODI
from logs.log import logger
from bot.bot_engine import get_bot_throw

UI_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(UI_DIR, "dart_settings.json")


class ProDartLeague(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(700, 400)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        center_point = self.screen().availableGeometry().center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        self.setStyleSheet(MAIN_STYLE)
        self.players, self.scores, self.has_entered = [], [], []
        self.finished_players = []
        self.last_darts = []
        self.is_bust = []
        self.history = []
        self.num_buttons = []
        self.current_player_idx = 0
        self.darts_thrown = 0
        self.modifier = 1
        self.game_mode = "301"
        self.bot_timer = QTimer()
        self.bot_timer.setSingleShot(True)
        self.bot_timer.timeout.connect(self.execute_bot_throw)
        self.typed_score = ""
        self.turn_timer = QTimer()
        self.turn_timer.setSingleShot(True)
        self.turn_timer.timeout.connect(self.next_player)
        self.stack = QStackedWidget()
        self.match_log = []
        self.player_map = {}

        self.stack.addWidget(create_setup_ui(self))
        self.stack.addWidget(create_game_ui(self))
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self.stats_btn.clicked.connect(self.open_stats_window)
        self.load_settings()

    def execute_bot_throw(self):
        if self.stack.currentIndex() != 1:
            return

        p = self.current_player_idx
        current_name = self.players[p]

        bot_type = self.player_map.get(current_name, "Mensch")
        if bot_type == "Mensch":
            return

        current_score = self.scores[p]

        is_double_in = not self.has_entered[p]
        is_double_out = self.double_out

        aktuelle_variante = self.variant_box.currentText() if hasattr(self, 'variant_box') else "Standard"

        val, mod = get_bot_throw(
            self.game_mode,
            current_score,
            bot_type,
            self.match_log,
            self.player_map,
            double_in=is_double_in,
            double_out=is_double_out,
            variante=aktuelle_variante
        )

        self.modifier = mod
        self.num_clicked(val)
        if p in self.finished_players or len(self.finished_players) > 0:
            return
        next_name = self.players[self.current_player_idx]
        next_type = self.player_map.get(next_name, "Mensch")
        if self.darts_thrown < 3 and not self.is_bust[p] and p not in self.finished_players and next_type != "Mensch":
            self.bot_timer.start(1000)

    def open_stats_window(self):
        self.stats_win = StatsWindow()
        self.hide()
        self.stats_win.destroyed.connect(lambda: self.show())
        self.stats_win.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.stats_win.show()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        return
                    saved_names = data.get("names", [])
                    if isinstance(saved_names, list):
                        for i, name in enumerate(saved_names):
                            if i < len(self.player_inputs) and isinstance(name, str):
                                self.player_inputs[i].setText(name)
                    saved_bots = data.get("bot_types", [])
                    if isinstance(saved_bots, list):
                        for i, b_type in enumerate(saved_bots):
                            if i < len(self.bot_types) and isinstance(b_type, str):
                                self.bot_types[i].setCurrentText(b_type)
                    self.mode_box.setCurrentText(str(data.get("mode", "Classic X01")))
                    self.variant_box.setCurrentText(str(data.get("variant", "501")))
                    self.cb_double_in.setChecked(bool(data.get("double_in", False)))
                    self.cb_double_out.setChecked(bool(data.get("double_out", False)))
                    self.cb_randomize.setChecked(bool(data.get("randomize", False)))
                    self.cb_play_to_end.setChecked(bool(data.get("play_to_end", False)))

            except (json.JSONDecodeError, OSError, AttributeError):
                pass

    def save_settings(self):
        data = {
            "names": [inp.text().strip() for inp in self.player_inputs],
            "bot_types": [combo.currentText() for combo in self.bot_types],
            "mode": self.mode_box.currentText(),
            "variant": self.variant_box.currentText(),
            "double_in": self.cb_double_in.isChecked(),
            "double_out": self.cb_double_out.isChecked(),
            "randomize": self.cb_randomize.isChecked(),
            "play_to_end": self.cb_play_to_end.isChecked()
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def keyPressEvent(self, event: QKeyEvent):
        if self.stack.currentIndex() != 1 or not self.btn_double.isEnabled():
            return
        key = event.key()
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            temp_input = self.typed_score + chr(key)
            val = int(temp_input)
            if val <= 20 or val == 25 or val == 50:
                self.typed_score = temp_input
                self.update_keyboard_feedback()
            else:
                self.score_label.setText("LIMIT")
                self.score_label.setStyleSheet("font-size: 90px; font-weight: bold; color: #ff4c4c;")
                QTimer.singleShot(500, self.update_display)
                self.typed_score = ""
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.typed_score:
                val = int(self.typed_score)
                if val == 50:
                    self.modifier = 2
                    self.num_clicked(25)
                else:
                    self.num_clicked(val)
                self.typed_score = ""
                self.update_display()
        elif key == Qt.Key.Key_Backspace:
            if self.typed_score:
                self.typed_score = self.typed_score[:-1]
                if not self.typed_score: self.update_display()
                else: self.update_keyboard_feedback()
            else:
                self.undo_hit()
        elif key == Qt.Key.Key_D:
            self.btn_double.click()
        elif key == Qt.Key.Key_T:
            self.btn_triple.click()

    def update_keyboard_feedback(self):
        if self.typed_score:
            self.score_label.setText(self.typed_score)
            self.score_label.setStyleSheet("font-size: 90px; font-weight: bold; color: #fdbc4b;")
        else:
            self.update_display()

    def hit_bullseye(self):
        self.modifier = 2
        self.num_clicked(25)

    def start_game(self):
        temp_map = {}
        for i, inp in enumerate(self.player_inputs):
            name = inp.text().strip()
            if name and i < len(self.bot_types):
                temp_map[name] = self.bot_types[i].currentText()

        self.save_settings()
        names = [inp.text().strip() for inp in self.player_inputs if inp.text().strip()]
        if not names:
            names = ["Spieler 1"]
            temp_map["Spieler 1"] = "Mensch"

        if self.cb_randomize.isChecked():
            random.shuffle(names)

        self.players = names[:8]

        self.player_map = {name: temp_map.get(name, "Mensch") for name in self.players}

        haupt_modus = self.mode_box.currentText()
        variante = self.variant_box.currentText()
        hat_varianten = False
        is_x01_type = True
        if haupt_modus in SPIEL_MODI:
            hat_varianten = SPIEL_MODI[haupt_modus][2] is not None
            if len(SPIEL_MODI[haupt_modus]) > 3:
                is_x01_type = SPIEL_MODI[haupt_modus][3]
        if hat_varianten:
            basis_modus = haupt_modus.replace(" X01", "")
            self.game_mode = f"{basis_modus} {variante}"
        else:
            self.game_mode = haupt_modus

        self.limit = 301
        if haupt_modus in SPIEL_MODI:
            SPIEL_MODI[haupt_modus][1](self)
        self.start_score_val = self.scores[0]
        self.is_bust = [False] * len(self.players)
        if is_x01_type:
            self.has_entered = [not self.cb_double_in.isChecked()] * len(self.players)
        else:
            self.has_entered = [True] * len(self.players)
        self.last_darts = [[] for _ in range(len(self.players))]
        self.finished_players = []
        self.double_out = self.cb_double_out.isChecked() if is_x01_type else False
        self.current_player_idx = 0
        self.darts_thrown = 0
        self.history = []
        self.modifier = 1
        self.typed_score = ""
        self.score_at_start_of_turn = self.scores[0]
        self.table.setRowCount(len(self.players))
        self.set_buttons_enabled(True)
        self.match_log = []
        self.update_display()
        QTimer.singleShot(1, self.switch_to_game_window)

        first_player = self.players[0]
        if self.player_map.get(first_player, "Mensch") != "Mensch":
            self.set_buttons_enabled(False)
            self.bot_timer.start(1500)

    def switch_to_game_window(self):
        screen_geo = self.screen().availableGeometry()
        width = min(1280, screen_geo.width())
        height = min(768, screen_geo.height())
        new_x = screen_geo.x() + (screen_geo.width() - width) // 2
        new_y = screen_geo.y() + (screen_geo.height() - height) // 2
        self.hide()
        self.stack.setCurrentIndex(1)
        self.setGeometry(new_x, new_y, width, height)
        self.show()
        QApplication.processEvents()
        self.effect = QGraphicsOpacityEffect()
        self.stack.currentWidget().setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        self.setFocus()

    def cancel_game(self):
        self.bot_timer.stop()
        self.turn_timer.stop()
        QTimer.singleShot(1, self.switch_to_setup_window)

    def switch_to_setup_window(self):
        screen_geo = self.screen().availableGeometry()
        target_w, target_h = 700, 400
        new_x = screen_geo.x() + (screen_geo.width() - target_w) // 2
        new_y = screen_geo.y() + (screen_geo.height() - target_h) // 2
        self.hide()
        self.stack.setCurrentIndex(0)
        self.setGeometry(new_x, new_y, target_w, target_h)
        self.show()
        QApplication.processEvents()
        self.setup_effect = QGraphicsOpacityEffect()
        self.stack.currentWidget().setGraphicsEffect(self.setup_effect)
        self.setup_animation = QPropertyAnimation(self.setup_effect, b"opacity")
        self.setup_animation.setDuration(500)
        self.setup_animation.setStartValue(0)
        self.setup_animation.setEndValue(1)
        self.setup_animation.start()

    def set_buttons_enabled(self, enabled):
        for btn in self.num_buttons:
            btn.setEnabled(enabled)
        if hasattr(self, 'btn_double'): self.btn_double.setEnabled(enabled)
        if hasattr(self, 'btn_triple'): self.btn_triple.setEnabled(enabled)

    def mod_clicked(self):
        sender = self.sender()
        if sender == self.btn_double and self.btn_double.isChecked(): self.btn_triple.setChecked(False); self.modifier = 2
        elif sender == self.btn_triple and self.btn_triple.isChecked(): self.btn_double.setChecked(False); self.modifier = 3
        else: self.modifier = 1

    def num_clicked(self, val):
        if self.darts_thrown == 0:
            self.busted_before_turn = list(self.is_bust)

        if not hasattr(self, 'current_turn_kill'):
            self.current_turn_kill = False

        state = (list(self.scores), list(self.has_entered), self.current_player_idx, self.darts_thrown, self.score_at_start_of_turn, [list(d) for d in self.last_darts], list(self.is_bust), list(self.finished_players), list(self.match_log), self.current_turn_kill)
        self.history.append(state)

        haupt_modus = self.mode_box.currentText()
        is_x01_type = True
        if haupt_modus in SPIEL_MODI and len(SPIEL_MODI[haupt_modus]) > 3:
            is_x01_type = SPIEL_MODI[haupt_modus][3]
        if self.darts_thrown == 0:
            if is_x01_type:
                self.is_bust[self.current_player_idx] = False
            self.last_darts[self.current_player_idx] = []
        if val == 0 or self.modifier == "Miss":
            val = 0
            self.modifier = 1
            dart_str = "Miss"
        else:
            if val == 25 and self.modifier == 3:
                self.modifier = 1
            prefix = "D" if self.modifier == 2 else "T" if self.modifier == 3 else ""
            dart_str = f"{prefix}{val}" if val != 25 else ("BULL" if self.modifier == 1 else "D-BULL")
        points = val * self.modifier
        was_double = (self.modifier == 2)
        self.last_darts[self.current_player_idx].append(dart_str)
        daten = {
            "val": val,
            "points": points,
            "was_double": was_double,
            "was_triple": (self.modifier == 3)
        }
        self.match_log.append({
            "spieler": self.players[self.current_player_idx],
            "wurf": dart_str,
            "wert": val,
            "multiplikator": self.modifier
        })
        modus_daten = SPIEL_MODI.get(haupt_modus)
        if modus_daten:
            verarbeitungs_funktion = modus_daten[0]
            verarbeitungs_funktion(self, daten)

        busted_before = getattr(self, "busted_before_turn", [False] * len(self.players))
        for i in range(len(self.players)):
            if self.is_bust[i] and not busted_before[i]:
                self.current_turn_kill = True

        self.btn_double.setChecked(False)
        self.btn_triple.setChecked(False)
        self.modifier = 1
        self.typed_score = ""

    def finish_dart(self):
        self.darts_thrown += 1
        if self.darts_thrown == 3:
            self.wait_and_next_player()
        else:
            self.update_display()

    def wait_and_next_player(self):
        self.update_display()
        self.set_buttons_enabled(False)
        self.turn_timer.start(1000)

    def next_player(self):
        if self.cb_play_to_end.isChecked():
            game_over = len(self.finished_players) >= len(self.players) - 1 or \
                        (len(self.players) == 1 and len(self.finished_players) == 1)
        else:
            game_over = len(self.finished_players) > 0
        if game_over:
            # Absolute Notbremse für alle Bot-Aktivitäten:
            self.bot_timer.stop()
            self.turn_timer.stop()

            try:
                platzierungen = {}
                if self.cb_play_to_end.isChecked():
                    for i in range(len(self.players)):
                        if i not in self.finished_players:
                            self.finished_players.append(i)
                    for idx, p_idx in enumerate(self.finished_players):
                        platzierungen[self.players[p_idx]] = idx + 1
                else:
                    for idx, spieler_name in enumerate(self.players):
                        if idx in self.finished_players:
                            platzierungen[spieler_name] = self.finished_players.index(idx) + 1
                        else:
                            platzierungen[spieler_name] = -1
                match_data = {
                    "datum": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "modus": self.game_mode,
                    "gewinner": self.players[self.finished_players[0]] if self.finished_players else self.players[0],
                    "platzierungen": platzierungen,
                    "teilnehmer": self.players,
                    "verlauf": self.match_log
                }
                os.makedirs("stats", exist_ok=True)
                dateiname = f"stats/match_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(dateiname, "w", encoding="utf-8") as f:
                    json.dump(match_data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Fehler beim Speichern der Statistik: {e}", exc_info=True)

            self.score_label.setText("FINISH!")
            self.score_label.setStyleSheet("font-size: 80px; font-weight: bold; color: #27ae60;")

            # Wichtig, damit die GUI wieder reagiert und man das Spiel verlassen kann:
            if hasattr(self, 'info_label'):
                self.info_label.setText("Spiel beendet")
            self.back_btn.setEnabled(True)
            self.back_btn.setText("Beenden")
            self.back_btn.setStyleSheet("background-color: #27ae60; color: black; font-weight: bold; height: 35px;")

            # 1. Zuerst alle Dart-Eingabebuttons sperren
            self.set_buttons_enabled(False)

            # 2. JETZT den Beenden-Button explizit und als allerletztes aktivieren!
            if hasattr(self, 'back_btn'):
                self.back_btn.setEnabled(True)
                self.back_btn.setVisible(True)
                self.back_btn.setText("Beenden")
                self.back_btn.setStyleSheet("background-color: #27ae60; color: black; font-weight: bold; height: 35px;")
                self.back_btn.setFocus()
            return

        self.darts_thrown = 0
        self.current_turn_kill = False

        while True:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            if self.current_player_idx not in self.finished_players:
                break

        self.is_bust[self.current_player_idx] = False

        self.score_at_start_of_turn = self.scores[self.current_player_idx]
        self.update_display()

        current_name = self.players[self.current_player_idx]
        if self.player_map.get(current_name, "Mensch") != "Mensch":
            self.set_buttons_enabled(False)
            self.bot_timer.start(1500)
        else:
            self.set_buttons_enabled(True)

    def undo_hit(self):
        if not self.history: return
        self.turn_timer.stop()
        self.bot_timer.stop()
        state = self.history.pop()
        (self.scores, self.has_entered, self.current_player_idx, self.darts_thrown, self.score_at_start_of_turn, self.last_darts, self.is_bust, self.finished_players, self.match_log, self.current_turn_kill) = state

        current_name = self.players[self.current_player_idx]
        if self.player_map.get(current_name, "Mensch") != "Mensch":
            self.set_buttons_enabled(False)
            self.bot_timer.start(1500)
        else:
            self.set_buttons_enabled(True)
        self.update_display()

    def update_display(self):
        p = self.current_player_idx
        haupt_modus = self.mode_box.currentText()
        ui_behavior = SPIEL_MODI[haupt_modus][4] if haupt_modus in SPIEL_MODI and len(SPIEL_MODI[haupt_modus]) > 4 else "standard"
        is_x01 = SPIEL_MODI[haupt_modus][3] if haupt_modus in SPIEL_MODI and len(SPIEL_MODI[haupt_modus]) > 3 else True
        target_val = self.scores[p]

        has_kill = (ui_behavior == "collision_detection") and getattr(self, "current_turn_kill", False)

        if has_kill and self.darts_thrown > 0:
            self.score_label.setText("KILL!")
            self.score_label.setStyleSheet("font-size: 70px; font-weight: bold; color: #e67e22;")
        else:
            if ui_behavior == "target_scoring":
                txt = "Ziel: BULL" if target_val == 25 else f"Ziel: {target_val}"
            else:
                txt = str(target_val)
            self.score_label.setText(txt)
            self.score_label.setStyleSheet("font-size: 90px; font-weight: bold; color: #3daee9;")
        hint = '(Warten auf Double-In)' if not self.has_entered[p] and is_x01 else ''
        game_widget = self.stack.widget(1)
        if hasattr(game_widget, 'info_label'):
            game_widget.info_label.setText(f"Spieler: {self.players[p]} {hint}")
        self.dart_label.setText("Darts: " + "● " * self.darts_thrown + "○ " * (3 - self.darts_thrown))
        for i in range(len(self.players)):
            for col in range(3):
                if not self.table.item(i, col):
                    self.table.setItem(i, col, QTableWidgetItem(""))
            ni = self.table.item(i, 0)
            li = self.table.item(i, 1)
            si = self.table.item(i, 2)
            ni.setText(self.players[i])
            ni.setForeground(QColor(Qt.GlobalColor.yellow) if i == p else QColor(Qt.GlobalColor.white))
            li.setText(", ".join(self.last_darts[i]))
            if i in self.finished_players:
                si_text = f"PLATZ {self.finished_players.index(i)+1}"
            elif ui_behavior == "life_tracking":
                zahl = getattr(self, "killer_numbers", [0]*len(self.players))[i]
                ist_killer = getattr(self, "killer_status", [False]*len(self.players))[i]
                if zahl == 0:
                    si_text = "Wählen..."
                else:
                    si_text = f"{zahl} [K]" if ist_killer else f"{zahl}"
            else:
                si_text = str(self.scores[i])
            si.setText(si_text)
            if i in self.finished_players:
                si.setForeground(QColor("#fdbc4b"))
            elif self.is_bust[i]:
                si.setForeground(QColor("#ff4c4c"))
                li.setForeground(QColor("#ff4c4c"))
            else:
                si.setForeground(QColor(Qt.GlobalColor.white))
                li.setForeground(QColor(Qt.GlobalColor.white))
