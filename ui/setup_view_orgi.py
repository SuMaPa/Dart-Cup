import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QCheckBox, QGridLayout, QLineEdit, QPushButton, QDialog, QTextBrowser
from PyQt6.QtCore import Qt
from dart_cup import SPIEL_MODI
from ui.erklaerungen import MODI_TEXTE

def show_help_dialog(parent_widget):
    dialog = QDialog(parent_widget)
    dialog.setWindowTitle("Spielmodi & Erklärungen")
    dialog.resize(700, 500)
    dialog_layout = QVBoxLayout(dialog)
    text_browser = QTextBrowser(dialog)
    html_content = ""
    for modus, text in MODI_TEXTE.items():
        html_content += f"<h3><b style='color: #3daee9;'>{modus}</b></h3><p>{text}</p><br>"
    text_browser.setHtml(html_content)
    dialog_layout.addWidget(text_browser)
    close_btn = QPushButton("Schließen", dialog)
    close_btn.clicked.connect(dialog.accept)
    dialog_layout.addWidget(close_btn)
    dialog.exec()

def create_setup_ui(game):
    widget = QWidget()
    layout = QVBoxLayout()
    title = QLabel("DART SETUP")
    title.setStyleSheet("font-size: 28px; font-weight: bold; color: #3daee9; margin-top: 10px;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    mode_layout = QHBoxLayout()
    mode_layout.addWidget(QLabel("Modus:"))
    game.mode_box = QComboBox()
    game.mode_box.addItems(list(SPIEL_MODI.keys()))
    game.mode_box.setFixedWidth(280)
    mode_layout.addWidget(game.mode_box)
    mode_layout.addWidget(QLabel("Variante:"))
    game.variant_box = QComboBox()
    game.variant_box.addItems(SPIEL_MODI)
    game.variant_box.setFixedWidth(140)
    mode_layout.addWidget(game.variant_box)

    def on_mode_changed(text):
        modus_daten = SPIEL_MODI.get(text)

        # 1. Bestimmen, ob dieser Modus überhaupt Varianten besitzt
        varianten_liste = modus_daten[2] if modus_daten and len(modus_daten) > 2 else None
        aktiv = varianten_liste is not None

        # 2. Die Box leeren und NUR die passenden Varianten reinwerfen
        game.variant_box.clear()
        if aktiv:
            game.variant_box.addItems(varianten_liste)
        else:
            game.variant_box.addItems(["Standard"])

        # 3. UI-Zustand anpassen
        game.variant_box.setEnabled(aktiv)
        game.variant_box.setStyleSheet("") if aktiv else game.variant_box.setStyleSheet("color: #888888;")

        # Doppel-In/Out Logik
        is_x01 = modus_daten[3] if modus_daten and len(modus_daten) > 3 else True
        if hasattr(game, 'cb_double_in') and hasattr(game, 'cb_double_out'):
            if not is_x01:
                game.cb_double_in.setChecked(False)
                game.cb_double_out.setChecked(False)
                game.cb_double_in.setEnabled(False)
                game.cb_double_out.setEnabled(False)
            else:
                game.cb_double_in.setEnabled(True)
                game.cb_double_out.setEnabled(True)

    game.mode_box.currentTextChanged.connect(on_mode_changed)

    help_btn = QPushButton("?")
    help_btn.setFixedSize(24, 24)
    help_btn.setStyleSheet("""
        QPushButton {
            background-color: #3daee9;
            color: black;
            border-radius: 12px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #2a9cd6;
        }
    """)
    help_btn.clicked.connect(lambda: show_help_dialog(widget))
    mode_layout.addWidget(help_btn)
    layout.addLayout(mode_layout)
    rule_frame = QFrame()
    rule_layout = QHBoxLayout(rule_frame)
    game.cb_double_in = QCheckBox("Double In")
    game.cb_double_out = QCheckBox("Double Out")
    game.cb_randomize = QCheckBox("Randomize Player")
    game.cb_play_to_end = QCheckBox("Play to End")
    rule_layout.addWidget(game.cb_double_in)
    rule_layout.addWidget(game.cb_double_out)
    rule_layout.addWidget(game.cb_randomize)
    rule_layout.addWidget(game.cb_play_to_end)
    layout.addWidget(rule_frame)

    grid_names = QGridLayout()
    game.player_inputs = []
    game.bot_types = []

    for i in range(8):
        row = i // 2
        col_offset = (i % 2) * 2

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"Spieler {i+1}")
        line_edit.setFixedWidth(180)

        bot_combo = QComboBox()
        bot_combo.addItems(["Mensch", "Dynamisch", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10"])
        bot_combo.setFixedWidth(100)

        grid_names.addWidget(line_edit, row, col_offset)
        grid_names.addWidget(bot_combo, row, col_offset + 1)

        game.player_inputs.append(line_edit)
        game.bot_types.append(bot_combo)

    layout.addLayout(grid_names)
    layout.addStretch()

    bottom = QHBoxLayout()

    start_btn = QPushButton("GAME START")
    start_btn.setStyleSheet("background-color: #27ae60; padding-left: 15px; padding-right: 15px;")
    start_btn.clicked.connect(game.start_game)
    bottom.addWidget(start_btn)

    bottom.addStretch()
    game.stats_btn = QPushButton("Statistiken")
    game.stats_btn.setStyleSheet("background-color: #34495e; padding-left: 15px; padding-right: 15px;")
    bottom.addWidget(game.stats_btn)

    bottom.addSpacing(20)

    exit_btn = QPushButton("Programm beenden")
    exit_btn.setStyleSheet("padding-left: 15px; padding-right: 15px;")
    exit_btn.clicked.connect(sys.exit)
    bottom.addWidget(exit_btn)

    layout.addLayout(bottom)

    # Ganz wichtig: Erst aufrufen, wenn ALLE Layouts und Widgets final verknüpft sind!
    on_mode_changed(game.mode_box.currentText())

    widget.setLayout(layout)
    return widget
