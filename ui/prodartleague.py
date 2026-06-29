# ui/prodartleague.py
import importlib
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QGraphicsOpacityEffect,
    QTableWidgetItem,
    QApplication,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QColor, QKeyEvent

from ui.styles import MAIN_STYLE
from ui.setup_view import create_setup_ui
from ui.game_view import create_game_ui
from ui.stats_view import StatsWindow
from bot.bot_engine import get_bot_throw
from controller.game_controller import GameController
from ui.keyboard_handler import handle_key_press
from logs.stats_manager import load_settings_data, save_settings_data


class ProDartLeague(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = GameController(self)

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
        self.typed_score = ""

        self.bot_timer = QTimer()
        self.bot_timer.setSingleShot(True)
        self.bot_timer.timeout.connect(self.execute_bot_throw)

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

    def start_game(self):
        self.controller.start_game()

    def num_clicked(self, val):
        self.controller.num_clicked(val)

    def next_player(self):
        self.controller.next_player()

    def undo_hit(self):
        self.controller.undo_hit()

    def load_live_ui(self):
        self.live_widget = None  # Zurücksetzen, um alte Referenzen zu löschen
        for i in reversed(range(self.right_layout.count())):
            widget = self.right_layout.itemAt(i).widget()
            if widget is not None:
                if widget == self.table:
                    widget.hide()
                else:
                    widget.setParent(None)
                    widget.deleteLater()

        file_map = {
            "Cricket": "cricket",
            "Classic": "classic",
            "Elimination": "elimination",
            "Bob": "bob",
            "Killer": "killer",
            "Shanghai": "shanghai",
            "Halve It": "halve_it",
        }
        modul_datei = "classic"
        for key, val in file_map.items():
            if key in self.game_mode:
                modul_datei = val
                break

        if modul_datei == "classic":
            self.table.show()
            return

        try:
            spiel_modul = importlib.import_module(f"ui.spiel.{modul_datei}")
            if hasattr(spiel_modul, "get_live_widget"):
                self.live_widget = spiel_modul.get_live_widget(self)
                self.right_layout.addWidget(self.live_widget)
            else:
                # FALLBACK: Wenn das Modul kein eigenes Live-Widget bereitstellt,
                # blenden wir stattdessen die Standard-Tabelle wieder ein.
                self.table.show()
        except:
            self.table.show()

    def execute_bot_throw(self):
        if self.stack.currentIndex() != 1:
            return
        p = self.current_player_idx
        current_name = self.players[p]
        bot_type = self.player_map.get(current_name, "Mensch")
        if bot_type == "Mensch":
            return

        aktuelle_variante = (
            self.variant_box.currentText()
            if hasattr(self, "variant_box")
            else "Standard"
        )
        val, mod = get_bot_throw(
            self.game_mode,
            self.scores[p],
            bot_type,
            self.match_log,
            self.player_map,
            double_in=not self.has_entered[p],
            double_out=self.double_out,
            variante=aktuelle_variante,
        )
        self.modifier = mod
        self.num_clicked(val)

        # KORREKTUR: Nur wenn der AKTIVE Spieler (p) fertig ist, wird abgebrochen.
        # Die fehlerhafte, doppelte Zeile darunter wurde jetzt endgültig gelöscht.
        if p in self.finished_players:
            return

        next_name = self.players[self.current_player_idx]
        if (
            self.darts_thrown < 3
            and not self.is_bust[p]
            and p not in self.finished_players
            and self.player_map.get(next_name, "Mensch") != "Mensch"
        ):
            self.bot_timer.start(1000)

    def open_stats_window(self):
        self.stats_win = StatsWindow()
        self.hide()
        self.stats_win.destroyed.connect(lambda: self.show())
        self.stats_win.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.stats_win.show()

    def load_settings(self):
        data = load_settings_data()
        if not data:
            return
        try:
            for i, name in enumerate(data.get("names", [])):
                if i < len(self.player_inputs):
                    self.player_inputs[i].setText(name)
            for i, b_type in enumerate(data.get("bot_types", [])):
                if i < len(self.bot_types):
                    self.bot_types[i].setCurrentText(b_type)
            self.mode_box.setCurrentText(str(data.get("mode", "Classic X01")))
            self.variant_box.setCurrentText(str(data.get("variant", "501")))
            self.cb_double_in.setChecked(bool(data.get("double_in", False)))
            self.cb_double_out.setChecked(bool(data.get("double_out", False)))
            self.cb_randomize.setChecked(bool(data.get("randomize", False)))
            self.cb_play_to_end.setChecked(bool(data.get("play_to_end", False)))
        except:
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
            "play_to_end": self.cb_play_to_end.isChecked(),
        }
        save_settings_data(data)

    def keyPressEvent(self, event: QKeyEvent):
        handle_key_press(self, event)

    def hit_bullseye(self):
        self.modifier = 2
        self.num_clicked(25)

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

    def cancel_game(self):
        self.bot_timer.stop()
        self.turn_timer.stop()
        QTimer.singleShot(1, self.switch_to_setup_window)

    def switch_to_game_window(self):
        screen_geo = self.screen().availableGeometry()
        width, height = min(1280, screen_geo.width()), min(768, screen_geo.height())
        self.hide()
        self.stack.setCurrentIndex(1)
        self.setGeometry(
            screen_geo.x() + (screen_geo.width() - width) // 2,
            screen_geo.y() + (screen_geo.height() - height) // 2,
            width,
            height,
        )
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

    def switch_to_setup_window(self):
        screen_geo = self.screen().availableGeometry()
        target_w, target_h = 700, 400
        self.hide()
        self.stack.setCurrentIndex(0)
        self.setGeometry(
            screen_geo.x() + (screen_geo.width() - target_w) // 2,
            screen_geo.y() + (screen_geo.height() - target_h) // 2,
            target_w,
            target_h,
        )
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
        if hasattr(self, "btn_double"):
            self.btn_double.setEnabled(enabled)
        if hasattr(self, "btn_triple"):
            self.btn_triple.setEnabled(enabled)

    def mod_clicked(self):
        sender = self.sender()
        if sender == self.btn_double and self.btn_double.isChecked():
            self.btn_triple.setChecked(False)
            self.modifier = 2
        elif sender == self.btn_triple and self.btn_triple.isChecked():
            self.btn_double.setChecked(False)
            self.modifier = 3
        else:
            self.modifier = 1

    def update_display(self):
        from dart_cup import SPIEL_MODI

        p = self.current_player_idx
        haupt_modus = self.mode_box.currentText()
        ui_behavior = (
            SPIEL_MODI[haupt_modus][4]
            if haupt_modus in SPIEL_MODI and len(SPIEL_MODI[haupt_modus]) > 4
            else "standard"
        )
        is_x01 = (
            SPIEL_MODI[haupt_modus][3]
            if haupt_modus in SPIEL_MODI and len(SPIEL_MODI[haupt_modus]) > 3
            else True
        )
        if "Shanghai" in self.game_mode:
            if "Finish" in self.game_mode:
                target_val = 20
            else:
                target_val = getattr(self, "current_round", 1)
        else:
            target_val = self.scores[p]
        if hasattr(self, "mode_info_label"):
            self.mode_info_label.setText(f"Game: {self.game_mode}")
        if hasattr(self, "round_info_label"):
            self.round_info_label.setText(f"Runde: {getattr(self, 'current_round', 1)}")

        if (
            (ui_behavior == "collision_detection")
            and getattr(self, "current_turn_kill", False)
            and self.darts_thrown > 0
        ):
            self.score_label.setText("KILL!")
            self.score_label.setStyleSheet(
                "font-size: 70px; font-weight: bold; color: #e67e22;"
            )
        else:
            txt = (
                "Ziel: BULL"
                if ui_behavior == "target_scoring" and target_val == 25
                else (
                    f"Ziel: {target_val}"
                    if ui_behavior == "target_scoring"
                    else str(target_val)
                )
            )
            self.score_label.setText(txt)
            self.score_label.setStyleSheet(
                "font-size: 90px; font-weight: bold; color: #3daee9;"
            )

        hint = "(Warten auf Double-In)" if not self.has_entered[p] and is_x01 else ""
        game_widget = self.stack.widget(1)
        if hasattr(game_widget, "info_label"):
            game_widget.info_label.setText(f"Spieler: {self.players[p]} {hint}")
        self.dart_label.setText(
            "Darts: " + "● " * self.darts_thrown + "○ " * (3 - self.darts_thrown)
        )

        for i in range(len(self.players)):
            for col in range(3):
                if not self.table.item(i, col):
                    self.table.setItem(i, col, QTableWidgetItem(""))
            ni, li, si = (
                self.table.item(i, 0),
                self.table.item(i, 1),
                self.table.item(i, 2),
            )
            ni.setText(self.players[i])
            ni.setForeground(
                QColor(Qt.GlobalColor.yellow)
                if i == p
                else QColor(Qt.GlobalColor.white)
            )
            li.setText(", ".join(self.last_darts[i]))

            if i in self.finished_players:
                platz = self.finished_players.index(i) + 1
                si_text = f"PLATZ {platz}"
            elif ui_behavior == "life_tracking":
                zahl = getattr(self, "killer_numbers", [0] * len(self.players))[i]
                si_text = (
                    "Wählen..."
                    if zahl == 0
                    else (
                        f"{zahl} [K]"
                        if getattr(self, "killer_status", [False] * len(self.players))[
                            i
                        ]
                        else f"{zahl}"
                    )
                )
            else:
                si_text = str(self.scores[i])
            si.setText(si_text)

            if i in self.finished_players:
                if self.finished_players.index(i) == 0:
                    si.setForeground(QColor("#fdbc4b"))  # Goldgelb für Platz 1
                else:
                    si.setForeground(
                        QColor(Qt.GlobalColor.white)
                    )  # Weiß für alle weiteren Plätze
            elif self.is_bust[i]:
                si.setForeground(QColor("#ff4c4c"))
                li.setForeground(QColor("#ff4c4c"))
            else:
                si.setForeground(QColor(Qt.GlobalColor.white))
                li.setForeground(QColor(Qt.GlobalColor.white))

        if hasattr(self, "live_widget") and self.live_widget is not None:
            try:
                # Hier sind die file_maps für alle Live-Widgets synchronisiert
                file_map = {
                    "Cricket": "cricket",
                    "Classic": "classic",
                    "Elimination": "elimination",
                    "Bob": "bob",
                    "Killer": "killer",
                    "Shanghai": "shanghai",
                    "Halve It": "halve_it",
                }
                modul_datei = "classic"
                for key, val in file_map.items():
                    if key in self.game_mode:
                        modul_datei = val
                        break
                if modul_datei != "classic":
                    importlib.import_module(
                        f"ui.spiel.{modul_datei}"
                    ).update_live_widget(self, self.live_widget)
            except Exception as e:
                pass
