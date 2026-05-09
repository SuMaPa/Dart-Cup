import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QGridLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLineEdit, QCheckBox,
                             QStackedWidget, QFrame, QComboBox, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QColor

class ProDartLeague(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dart Cup")
        self.resize(700, 400)
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
            QToolTip {
                background-color: #31363b; color: #eff0f1;
                border: 1px solid #3daee9; padding: 5px;
            }
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

        self.turn_timer = QTimer()
        self.turn_timer.setSingleShot(True)
        self.turn_timer.timeout.connect(self.next_player)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_setup_ui())
        self.stack.addWidget(self.create_game_ui())

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

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
        self.mode_box.addItems(["301", "501", "701", "Around the Clock", "Elimination"])
        self.mode_box.setCurrentText("301")
        mode_layout.addWidget(self.mode_box)

        help_icon = QLabel("?")
        help_icon.setFixedSize(20, 20)
        help_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_icon.setStyleSheet("background-color: #3daee9; color: black; border-radius: 10px; font-weight: bold;")
        help_icon.setToolTip(            "<b>MODI ERKLÄRUNG:</b><br><br>"
            "<b>301/501/701:</b> Klassisch auf 0 runterspielen.<br>"
            "<b>Around the Clock:</b> Triff die Zahlen 1 bis 20 nacheinander, zum Schluss Bull.<br>"
            "<b>Elimination:</b> Starte bei 301. Erreichst du den Score eines Gegners, "
            "wird dieser auf 301 zurückgesetzt!")
        mode_layout.addWidget(help_icon)
        layout.addLayout(mode_layout)

        rule_frame = QFrame()
        rule_layout = QHBoxLayout(rule_frame)
        self.cb_double_in = QCheckBox("Double In")
        self.cb_double_out = QCheckBox("Double Out")
        rule_layout.addWidget(self.cb_double_in)
        rule_layout.addWidget(self.cb_double_out)
        layout.addWidget(rule_frame)

        layout.addWidget(QLabel("Spielernamen:"))
        grid_names = QGridLayout()
        grid_names.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.player_inputs = []

        for i in range(8):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Spieler {i+1}")
            line_edit.setMaxLength(32)
            line_edit.setFixedWidth(300)
            grid_names.addWidget(line_edit, i // 2, i % 2)
            self.player_inputs.append(line_edit)

        layout.addLayout(grid_names)
        layout.addStretch()

        bottom_layout = QHBoxLayout()
        start_btn = QPushButton("GAME START")
        start_btn.setStyleSheet("background-color: #27ae60; font-weight: bold; height: 35px;")
        start_btn.setFixedWidth(140)
        start_btn.clicked.connect(self.start_game)

        exit_btn = QPushButton("Programm beenden")
        exit_btn.setFixedWidth(140)
        exit_btn.setFixedHeight(35)
        exit_btn.clicked.connect(sys.exit)

        bottom_layout.addWidget(start_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(exit_btn)
        layout.addLayout(bottom_layout)

        widget.setLayout(layout)
        return widget

    def create_game_ui(self):
        widget = QWidget()
        layout = QHBoxLayout()
        left = QVBoxLayout()

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 22px; color: #fdbc4b;")
        self.score_label = QLabel("301")
        self.score_label.setStyleSheet("font-size: 90px; font-weight: bold; color: #3daee9;")
        self.dart_label = QLabel("Darts: ○ ○ ○")

        left.addWidget(self.info_label)
        left.addWidget(self.score_label)
        left.addWidget(self.dart_label)

        mod_layout = QHBoxLayout()
        self.btn_double = QPushButton("DOUBLE")
        self.btn_triple = QPushButton("TRIPLE")
        for b in [self.btn_double, self.btn_triple]:
            b.setCheckable(True)
            b.setStyleSheet("QPushButton { height: 45px; font-weight: bold; } "
                            "QPushButton:checked { background-color: #27ae60; border: 1px solid white; }")
            b.clicked.connect(self.mod_clicked)
            mod_layout.addWidget(b)
            self.num_buttons.append(b)
        left.addLayout(mod_layout)

        grid = QGridLayout()
        for i in range(1, 21):
            btn = QPushButton(str(i))
            btn.setFixedSize(60, 50)
            btn.clicked.connect(lambda ch, v=i: self.num_clicked(v))
            grid.addWidget(btn, (i-1)//7, (i-1)%7)
            self.num_buttons.append(btn)

        spec = QHBoxLayout()
        for t, v in [("25 / BULL", 25), ("MISS", 0)]:
            b = QPushButton(t)
            b.setStyleSheet("background-color: #454a4f; height: 50px; font-weight: bold;")
            b.clicked.connect(lambda ch, v=v: self.num_clicked(v))
            spec.addWidget(b)
            self.num_buttons.append(b)

        left.addLayout(grid)
        left.addLayout(spec)

        control_layout = QHBoxLayout()
        undo_btn = QPushButton("UNDO")
        undo_btn.setStyleSheet("background-color: #fdbc4b; color: black; font-weight: bold; height: 35px;")
        undo_btn.clicked.connect(self.undo_hit)

        self.back_btn = QPushButton("Abbrechen")
        self.back_btn.setStyleSheet("background-color: #454a4f; height: 35px;")
        self.back_btn.clicked.connect(self.cancel_game)

        control_layout.addWidget(undo_btn)
        control_layout.addWidget(self.back_btn)
        left.addLayout(control_layout)

        layout.addLayout(left, 3)

        right = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Spieler", "Letzte Würfe", "Score"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        right.addWidget(QLabel("SCOREBOARD"))
        right.addWidget(self.table)
        layout.addLayout(right, 2)

        widget.setLayout(layout)
        return widget

    def start_game(self):
        names = [inp.text().strip() for inp in self.player_inputs if inp.text().strip()]
        if not names: names = ["Spieler 1"]
        self.players = names[:8]

        self.game_mode = self.mode_box.currentText()
        if self.game_mode == "Around the Clock":
            self.scores = [1] * len(self.players)
        elif self.game_mode == "Elimination":
            self.scores = [301] * len(self.players)
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
        self.btn_double.setChecked(False)
        self.btn_triple.setChecked(False)
        self.score_at_start_of_turn = self.scores[0]

        self.back_btn.setText("Abbrechen")
        self.back_btn.setStyleSheet("background-color: #454a4f; height: 35px;")

        self.table.setRowCount(len(self.players))
        self.set_buttons_enabled(True)
        self.update_display()

        self.table.setRowCount(len(self.players))
        self.set_buttons_enabled(True)
        self.update_display()
        QTimer.singleShot(1, self.switch_to_game_window)

    def switch_to_game_window(self):
        # 1. Geometrie vorberechnen
        screen_geo = self.screen().availableGeometry()
        target_w = min(1280, screen_geo.width())
        target_h = min(768, screen_geo.height())
        
        new_x = screen_geo.x() + (screen_geo.width() - target_w) // 2
        new_y = screen_geo.y() + (screen_geo.height() - target_h) // 2

        # 2. Der "KDE-Killer": Kurz hide/show, um die KWin-Position zu resetten
        self.hide()
        
        # UI umschalten und Größe/Position setzen, während es unsichtbar ist
        self.stack.setCurrentIndex(1)
        self.setGeometry(new_x, new_y, target_w, target_h)
        
        self.show()

        # 3. Den Grafik-Stack und Events forcieren
        QApplication.processEvents()

        # 4. Fade-In Effekt (startet jetzt sauber an der neuen Position)
        self.effect = QGraphicsOpacityEffect()
        self.stack.currentWidget().setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

        # Fade-In Animation
        self.effect = QGraphicsOpacityEffect()
        self.stack.currentWidget().setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def cancel_game(self):
        self.turn_timer.stop()
        QTimer.singleShot(1, self.switch_to_setup_window)

    def switch_to_setup_window(self):
        # 1. Geometrie berechnen
        screen_geo = self.screen().availableGeometry()
        target_w, target_h = 700, 400
        new_x = screen_geo.x() + (screen_geo.width() - target_w) // 2
        new_y = screen_geo.y() + (screen_geo.height() - target_h) // 2

        # 2. KDE-Reset
        self.hide()
        self.stack.setCurrentIndex(0)
        self.setGeometry(new_x, new_y, target_w, target_h)
        self.show()

        # 3. Fade-In für das Setup
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

    def num_clicked(self, val):
        state = (list(self.scores), list(self.has_entered), self.current_player_idx,
                 self.darts_thrown, self.score_at_start_of_turn,
                 [list(d) for d in self.last_darts], list(self.is_bust), list(self.finished_players))
        self.history.append(state)

        prefix = "D" if self.modifier == 2 else "T" if self.modifier == 3 else ""
        dart_str = f"{prefix}{val}" if val != 25 else ("BULL" if self.modifier == 1 else "D-BULL")
        if val == 0: dart_str = "0"

        points = val * self.modifier
        was_double = (self.modifier == 2) or (val == 25 and self.modifier == 2)

        if self.darts_thrown == 0:
            self.last_darts[self.current_player_idx] = []
            self.is_bust[self.current_player_idx] = False

        self.last_darts[self.current_player_idx].append(dart_str)

        if self.game_mode == "Around the Clock":
            self.process_around_the_clock(val)
        else:
            self.process_classic(points, was_double)

        self.btn_double.setChecked(False)
        self.btn_triple.setChecked(False)
        self.modifier = 1

    def process_around_the_clock(self, val):
        p_idx = self.current_player_idx
        target = self.scores[p_idx]
        if val == target:
            if target == 25:
                self.scores[p_idx] = 0
                self.finished_players.append(p_idx)
                self.wait_and_next_player()
                return
            self.scores[p_idx] = target + 1 if target < 20 else 25
        self.finish_dart()

    def process_classic(self, points, was_double):
        p_idx = self.current_player_idx
        if not self.has_entered[p_idx]:
            if was_double: self.has_entered[p_idx] = True
            else: return self.finish_dart()

        new_score = self.scores[p_idx] - points

        if new_score == 0 and (not self.double_out or was_double):
            self.scores[p_idx] = 0
            self.finished_players.append(p_idx)
            self.wait_and_next_player()
            return

        bust = (new_score < 0) or (new_score == 1 and self.double_out) or (new_score == 0 and self.double_out and not was_double)
        if bust:
            self.scores[p_idx] = self.score_at_start_of_turn
            self.is_bust[p_idx] = True
            self.wait_and_next_player()
        else:
            self.scores[p_idx] = new_score
            if self.game_mode == "Elimination":
                self.check_elimination(p_idx, new_score)
            self.finish_dart()

    def check_elimination(self, current_idx, score):
        if score == self.start_score_val: return
        for i in range(len(self.players)):
            if i != current_idx and i not in self.finished_players and self.scores[i] == score:
                self.scores[i] = self.start_score_val
                self.is_bust[i] = True

    def finish_dart(self):
        self.darts_thrown += 1
        if self.darts_thrown == 3:
            self.wait_and_next_player()
        else:
            self.update_display()

    def wait_and_next_player(self):
        self.update_display()
        self.set_buttons_enabled(False)
        self.turn_timer.start(1500)

    def next_player(self):
        if (len(self.players) > 1 and len(self.finished_players) >= len(self.players) - 1) or \
           (len(self.players) == 1 and len(self.finished_players) == 1):

            self.score_label.setText("GAME OVER")
            self.info_label.setText("Alle fertig!")
            self.back_btn.setText("Beenden")
            self.back_btn.setStyleSheet("background-color: #27ae60; color: black; font-weight: bold; height: 35px;")
            return

        self.darts_thrown = 0

        while True:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            if self.current_player_idx not in self.finished_players:
                break

        self.score_at_start_of_turn = self.scores[self.current_player_idx]
        self.set_buttons_enabled(True)
        self.update_display()

    def undo_hit(self):
        self.turn_timer.stop()
        if not self.history: return
        state = self.history.pop()
        (self.scores, self.has_entered, self.current_player_idx, self.darts_thrown,
         self.score_at_start_of_turn, self.last_darts, self.is_bust, self.finished_players) = state

        self.back_btn.setText("Abbrechen")
        self.back_btn.setStyleSheet("background-color: #454a4f; height: 35px;")

        self.set_buttons_enabled(True)
        self.update_display()

    def update_display(self):
        p = self.current_player_idx
        mode = self.game_mode

        target_val = self.scores[p]
        if mode == "Around the Clock":
            display_score = "Ziel: BULL" if target_val == 25 else f"Ziel: {target_val}"
        else:
            display_score = str(target_val)

        self.info_label.setText(f"Spieler: {self.players[p]} {'(IN!)' if not self.has_entered[p] else ''}")
        self.score_label.setText(display_score)
        self.dart_label.setText("Darts: " + "● " * self.darts_thrown + "○ " * (3 - self.darts_thrown))

        for i, (n, s) in enumerate(zip(self.players, self.scores)):
            ni = QTableWidgetItem(n)
            s_text = str(s)

            if i in self.finished_players:
                rank = self.finished_players.index(i) + 1
                s_text = f"PLATZ {rank}"
            elif mode == "Around the Clock":
                s_text = "BULL" if s == 25 else f"Feld {s}"

            si = QTableWidgetItem(s_text)
            li = QTableWidgetItem(", ".join(self.last_darts[i]))

            if i == p: ni.setForeground(Qt.GlobalColor.yellow)
            else: ni.setForeground(Qt.GlobalColor.white)

            if i in self.finished_players:
                si.setForeground(QColor("#fdbc4b"))
            elif mode != "Around the Clock":
                active_scores = [self.scores[j] for j in range(len(self.players)) if j not in self.finished_players]
                min_score = min(active_scores) if active_scores else 0
                if s == min_score and s < self.start_score_val:
                    si.setForeground(QColor("#27ae60"))

            if self.is_bust[i] and i not in self.finished_players:
                si.setForeground(QColor("#ff4c4c"))
                li.setForeground(QColor("#ff4c4c"))

            self.table.setItem(i, 0, ni)
            self.table.setItem(i, 1, li)
            self.table.setItem(i, 2, si)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProDartLeague()
    ex.show()
    sys.exit(app.exec())
