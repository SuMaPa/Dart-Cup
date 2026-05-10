import sys, random, json, os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QGridLayout, QTableWidget,
                            QTableWidgetItem, QHeaderView, QLineEdit, QCheckBox,
                            QStackedWidget, QFrame, QComboBox, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QColor, QKeyEvent

SETTINGS_FILE = "dart_settings.json"

class ProDartLeague(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dart Cup")
        self.resize(700, 400)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        center_point = self.screen().availableGeometry().center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        self.setStyleSheet("""
            QWidget { background-color: #1b1e20; color: #eff0f1; font-family: 'Segoe UI', sans-serif; }
            QLineEdit, QComboBox {
                background-color: #2a2e32; border: 1px solid #3daee9;
                padding: 5px; border-radius: 4px; color: #eff0f1;
            }
            QPushButton { background-color: #31363b; border: 1px solid #4d4d4d; border-radius: 3px; min-height: 25px; }
            QPushButton:hover { background-color: #3daee9; color: black; }
            QPushButton:disabled { background-color: #1b1e20; color: #4d4d4d; border: 1px solid #2a2e32; }
            QTableWidget { background-color: #232629; gridline-color: #31363b; border: 1px solid #4d4d4d; outline: none; }
            QHeaderView::section { background-color: #31363b; color: #eff0f1; border: 1px solid #1b1e20; }
        """)
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
        self.turn_timer = QTimer()
        self.turn_timer.setSingleShot(True)
        self.turn_timer.timeout.connect(self.next_player)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_setup_ui())
        self.stack.addWidget(self.create_game_ui())
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    saved_names = data.get("names", [])
                    for i, name in enumerate(saved_names):
                        if i < len(self.player_inputs):
                            self.player_inputs[i].setText(name)
                    self.mode_box.setCurrentText(data.get("mode", "301"))
                    self.cb_double_in.setChecked(data.get("double_in", False))
                    self.cb_double_out.setChecked(data.get("double_out", False))
                    self.cb_randomize.setChecked(data.get("randomize", False))
            except: pass

    def save_settings(self):
        data = {
            "names": [inp.text().strip() for inp in self.player_inputs],
            "mode": self.mode_box.currentText(),
            "double_in": self.cb_double_in.isChecked(),
            "double_out": self.cb_double_out.isChecked(),
            "randomize": self.cb_randomize.isChecked()
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def create_setup_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()
        title = QLabel("DART SETUP")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #3daee9; margin-top: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Modus:"))
        self.mode_box = QComboBox()
        self.mode_box.addItems(["301", "501", "701", "Around the Clock", "Mensch-ärgere-dich-nicht!", "Elimination"])
        mode_layout.addWidget(self.mode_box)
        help_icon = QLabel("?")
        help_icon.setFixedSize(20, 20)
        help_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_icon.setStyleSheet("background-color: #3daee9; color: black; border-radius: 10px; font-weight: bold;")
        help_icon.setToolTip(            "<b>MODI ERKLÄRUNG:</b><br><br>"
            "<b>301/501/701:</b> Klassisch auf 0 runterspielen.<br>"
            "<b>Around the Clock:</b> Triff die Zahlen 1 bis 20 nacheinander, zum Schluss Bull.<br>"
            "<b>Mensch-ärgere-dich-nicht!:</b><br> Starte bei 0. Ist irgendein Wurf der selbe Score wie der eines Gegners, "
            "wird dieser auf 0 zurückgesetzt!<br>"
            "<b>Elimination:</b><br> Starte bei 0. Ist beim 3. Wurf der gleiche Score wie der eines Gegners, "
            "wird dieser auf 0 zurückgesetzt!")
        mode_layout.addWidget(help_icon)
        layout.addLayout(mode_layout)

        rule_frame = QFrame()
        rule_layout = QHBoxLayout(rule_frame)
        self.cb_double_in = QCheckBox("Double In")
        self.cb_double_out = QCheckBox("Double Out")
        self.cb_randomize = QCheckBox("Randomize")
        rule_layout.addWidget(self.cb_double_in); rule_layout.addWidget(self.cb_double_out); rule_layout.addWidget(self.cb_randomize)
        layout.addWidget(rule_frame)
        grid_names = QGridLayout()
        self.player_inputs = []
        for i in range(8):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Spieler {i+1}")
            line_edit.setFixedWidth(300)
            grid_names.addWidget(line_edit, i // 2, i % 2)
            self.player_inputs.append(line_edit)
        layout.addLayout(grid_names)
        layout.addStretch()
        bottom = QHBoxLayout()
        start_btn = QPushButton("GAME START")
        start_btn.setStyleSheet("background-color: #27ae60; font-weight: bold; height: 35px;")
        start_btn.clicked.connect(self.start_game)
        exit_btn = QPushButton("Programm beenden")
        exit_btn.clicked.connect(sys.exit)
        bottom.addWidget(start_btn); bottom.addStretch(); bottom.addWidget(exit_btn)
        layout.addLayout(bottom)
        widget.setLayout(layout)
        return widget

    def create_game_ui(self):
        widget = QWidget()
        layout = QHBoxLayout()
        left = QVBoxLayout()
        self.info_label = QLabel("")
        self.score_label = QLabel("301")
        self.score_label.setStyleSheet("font-size: 90px; font-weight: bold; color: #3daee9;")
        self.dart_label = QLabel("Darts: ○ ○ ○")
        left.addWidget(self.info_label); left.addWidget(self.score_label); left.addWidget(self.dart_label)
        mod_layout = QHBoxLayout()
        self.btn_double = QPushButton("DOUBLE (D)"); self.btn_triple = QPushButton("TRIPLE (T)")
        for b in [self.btn_double, self.btn_triple]:
            b.setCheckable(True)
            b.setStyleSheet("QPushButton:checked { background-color: #27ae60; border: 1px solid white; }")
            b.clicked.connect(self.mod_clicked)
            mod_layout.addWidget(b); self.num_buttons.append(b)
        left.addLayout(mod_layout)
        grid = QGridLayout()
        for i in range(1, 21):
            btn = QPushButton(str(i)); btn.setFixedSize(60, 50)
            btn.clicked.connect(lambda ch, v=i: self.num_clicked(v))
            grid.addWidget(btn, (i-1)//7, (i-1)%7); self.num_buttons.append(btn)
        btn_zero = QPushButton("0")
        btn_zero.setFixedSize(60, 50)
        btn_zero.setStyleSheet("background-color: #5d6368; font-weight: bold;")
        btn_zero.clicked.connect(lambda: self.num_clicked(0))
        grid.addWidget(btn_zero, 2, 6); self.num_buttons.append(btn_zero)
        left.addLayout(grid)
        spec = QHBoxLayout()
        btn_25 = QPushButton("BULL")
        btn_25.setStyleSheet("background-color: #454a4f; height: 50px; font-weight: bold;")
        btn_25.clicked.connect(lambda: self.num_clicked(25))
        btn_bullseye = QPushButton("BULLSEYE")
        btn_bullseye.setStyleSheet("background-color: #454a4f; height: 50px; font-weight: bold;")
        btn_bullseye.clicked.connect(self.hit_bullseye)
        spec.addWidget(btn_25); spec.addWidget(btn_bullseye)
        self.num_buttons.extend([btn_25, btn_bullseye])
        left.addLayout(spec)
        ctrl = QHBoxLayout()
        undo_btn = QPushButton("Korrektur (Back)")
        undo_btn.setStyleSheet("QPushButton { background-color: #fdbc4b; color: black; font-weight: bold; height: 35px; } QPushButton:disabled { background-color: #554422; color: #888888; }")
        undo_btn.clicked.connect(self.undo_hit)
        self.back_btn = QPushButton("Abbrechen")
        self.back_btn.setStyleSheet("background-color: #454a4f; height: 35px;")
        self.back_btn.clicked.connect(self.cancel_game)
        ctrl.addWidget(undo_btn); ctrl.addWidget(self.back_btn)
        self.num_buttons.extend([undo_btn, self.back_btn])
        left.addLayout(ctrl)
        layout.addLayout(left, 3)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Spieler", "Letzte Würfe", "Score"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 2)
        widget.setLayout(layout)
        return widget

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
        self.save_settings()
        names = [inp.text().strip() for inp in self.player_inputs if inp.text().strip()]
        if not names:
            names = ["Spieler 1"]
        if self.cb_randomize.isChecked():
            random.shuffle(names)

        self.players = names[:8]
        self.game_mode = self.mode_box.currentText()
        self.limit = 301
        if "Elimination" in self.game_mode or "Mensch" in self.game_mode:
            self.scores = [0] * len(self.players)
        elif self.game_mode == "Around the Clock":
            self.scores = [1] * len(self.players)
        else:
            self.scores = [int(self.game_mode)] * len(self.players)
        self.start_score_val = self.scores[0]
        self.has_entered = [not self.cb_double_in.isChecked()] * len(self.players)
        self.last_darts = [[] for _ in range(len(self.players))]
        self.is_bust = [False] * len(self.players)
        self.finished_players = []
        self.double_out = self.cb_double_out.isChecked()
        self.current_player_idx = 0
        self.darts_thrown = 0
        self.history = []
        self.modifier = 1
        self.typed_score = ""
        self.score_at_start_of_turn = self.scores[0]
        self.table.setRowCount(len(self.players))
        self.set_buttons_enabled(True)
        self.update_display()
        QTimer.singleShot(1, self.switch_to_game_window)

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
        for btn in self.num_buttons: btn.setEnabled(enabled)

    def mod_clicked(self):
        sender = self.sender()
        if sender == self.btn_double and self.btn_double.isChecked(): self.btn_triple.setChecked(False); self.modifier = 2
        elif sender == self.btn_triple and self.btn_triple.isChecked(): self.btn_double.setChecked(False); self.modifier = 3
        else: self.modifier = 1

    def num_clicked(self, val):
        state = (list(self.scores), list(self.has_entered), self.current_player_idx, self.darts_thrown, self.score_at_start_of_turn, [list(d) for d in self.last_darts], list(self.is_bust), list(self.finished_players))
        self.history.append(state)
        if self.darts_thrown == 0:
            self.is_bust[self.current_player_idx] = False
            self.last_darts[self.current_player_idx] = []
        if val == 25 and self.modifier == 3: self.modifier = 1
        prefix = "D" if self.modifier == 2 else "T" if self.modifier == 3 else ""
        dart_str = f"{prefix}{val}" if val != 25 else ("BULL" if self.modifier == 1 else "D-BULL")
        if val == 0: dart_str = "0"
        points = val * self.modifier
        was_double = (self.modifier == 2)
        self.last_darts[self.current_player_idx].append(dart_str)
        if self.game_mode == "Around the Clock": self.process_around_the_clock(val)
        else: self.process_classic(points, was_double)
        self.btn_double.setChecked(False); self.btn_triple.setChecked(False); self.modifier = 1
        self.typed_score = ""

    def process_around_the_clock(self, val):
        p = self.current_player_idx
        if val == self.scores[p]:
            if val == 25: self.scores[p] = 0; self.finished_players.append(p); self.darts_thrown += 1; self.wait_and_next_player(); return
            self.scores[p] = val + 1 if val < 20 else 25
        self.finish_dart()

    def process_classic(self, points, was_double):
        p = self.current_player_idx
        is_elimination = "Elimination" in self.game_mode or "Mensch" in self.game_mode
        if not self.has_entered[p]:
            if was_double: self.has_entered[p] = True
            else: self.finish_dart(); return
        if is_elimination:
            new_score = self.scores[p] + points
            if new_score > self.limit:
                self.scores[p] = self.score_at_start_of_turn
                self.is_bust[p] = True
                self.darts_thrown += 1
                self.wait_and_next_player(); return
        else:
            new_score = self.scores[p] - points
        win_score = self.limit if is_elimination else 0
        if new_score == win_score and (not self.double_out or was_double):
            self.scores[p] = win_score
            self.finished_players.append(p)
            self.wait_and_next_player(); return
        if not is_elimination:
            if (new_score < 0) or (new_score == 1 and self.double_out) or (new_score == 0 and self.double_out and not was_double):
                self.scores[p] = self.score_at_start_of_turn
                self.is_bust[p] = True
                self.darts_thrown += 1
                self.wait_and_next_player(); return
        self.scores[p] = new_score
        if self.game_mode == "Mensch-ärgere-dich-nicht!": self.check_elimination(p, new_score)
        self.finish_dart()

    def check_elimination(self, current_idx, score):
        if score == 0: return
        for i in range(len(self.players)):
            if i != current_idx and i not in self.finished_players and self.scores[i] == score:
                self.scores[i] = 0
                self.is_bust[i] = True

    def finish_dart(self):
        self.darts_thrown += 1
        if self.darts_thrown == 3:
            if self.game_mode == "Elimination": self.check_elimination(self.current_player_idx, self.scores[self.current_player_idx])
            self.wait_and_next_player()
        else: self.update_display()

    def wait_and_next_player(self):
        self.update_display(); self.set_buttons_enabled(False); self.turn_timer.start(1000)

    def next_player(self):
        if len(self.finished_players) >= len(self.players): return
        self.darts_thrown = 0
        while True:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            if self.current_player_idx not in self.finished_players: break
        self.score_at_start_of_turn = self.scores[self.current_player_idx]
        self.set_buttons_enabled(True); self.update_display()

    def undo_hit(self):
        if not self.history: return
        self.turn_timer.stop()
        state = self.history.pop()
        (self.scores, self.has_entered, self.current_player_idx, self.darts_thrown, self.score_at_start_of_turn, self.last_darts, self.is_bust, self.finished_players) = state
        self.set_buttons_enabled(True); self.update_display()

    def update_display(self):
        p = self.current_player_idx
        mode, target_val = self.game_mode, self.scores[p]
        has_haha = any(i != p and self.is_bust[i] for i in range(len(self.players))) if "Elimination" in mode or "Mensch" in mode else False
        if has_haha and self.darts_thrown > 0:
            msg = "HAHA!" if "Mensch" in mode else "KILL!"
            self.score_label.setText(msg); self.score_label.setStyleSheet("font-size: 70px; font-weight: bold; color: #e67e22;")
        else:
            if mode == "Around the Clock": txt = "Ziel: BULL" if target_val == 25 else f"Ziel: {target_val}"
            else: txt = str(target_val)
            self.score_label.setText(txt); self.score_label.setStyleSheet("font-size: 90px; font-weight: bold; color: #3daee9;")
        self.info_label.setText(f"Spieler: {self.players[p]} {'(Warten auf Double-In)' if not self.has_entered[p] else ''}")
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

            si_text = f"PLATZ {self.finished_players.index(i)+1}" if i in self.finished_players else str(self.scores[i])
            si.setText(si_text)

            if i in self.finished_players:
                si.setForeground(QColor("#fdbc4b"))
            elif self.is_bust[i]:
                si.setForeground(QColor("#ff4c4c"))
                li.setForeground(QColor("#ff4c4c"))
            else:
                si.setForeground(QColor(Qt.GlobalColor.white))
                li.setForeground(QColor(Qt.GlobalColor.white))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProDartLeague()
    ex.show()
    sys.exit(app.exec())
