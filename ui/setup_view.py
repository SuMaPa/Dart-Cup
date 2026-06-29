# ui/setup_view.py
import sys, os, re
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QDialog,
    QTextBrowser,
)
from PyQt6.QtCore import Qt


def load_game_modes(file_name="game_modi.txt"):
    """Liest die Spielmodi-Datei über ein sicheres Tag-System ein (unterstützt mehrzeilige Beschreibungen)."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)

    if not os.path.exists(file_path):
        return {"Fehler": f"Datei nicht gefunden unter: {file_path}"}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        modi = {}
        current_mode = None
        is_reading_text = False

        # Zeilenweise durchgehen
        for line in content.splitlines():
            stripped_line = line.strip()

            # Neuer Modus-Block beginnt
            if stripped_line.startswith("[MODUS]"):
                current_mode = stripped_line.replace("[MODUS]", "").strip()
                modi[current_mode] = []
                is_reading_text = False
                continue

            # Text-Block beginnt
            if stripped_line.startswith("[TEXT]") and current_mode is not None:
                text_part = stripped_line.replace("[TEXT]", "").strip()
                modi[current_mode].append(text_part)
                is_reading_text = True
                continue

            # Folgezeilen des Textes einlesen (auch leere Zeilen für Absätze erhalten)
            if is_reading_text and current_mode is not None:
                modi[current_mode].append(stripped_line)

        # Zeilen bereinigen und formatieren
        formatted_modi = {}
        for mode, lines in modi.items():
            # Überflüssige Leerzeilen am Anfang und Ende des Blocks entfernen
            while lines and not lines[0]:
                lines.pop(0)
            while lines and not lines[-1]:
                lines.pop()

            # Verbindet alle Zeilen mit einem HTML-Umbruch, damit Zeilenumbrüche erhalten bleiben
            raw_text = "\n".join(lines)
            html_text = raw_text.replace("\n", "<br>")
            formatted_modi[mode] = html_text

        return formatted_modi
    except Exception as e:
        return {"Fehler": f"Datei konnte nicht gelesen werden: {e}"}


def show_help_dialog(parent_widget, mode_name):
    modi_help = load_game_modes()
    help_text = modi_help.get(
        mode_name, "Keine Beschreibung für diesen Modus verfügbar."
    )

    dialog = QDialog(parent_widget)
    dialog.setWindowTitle(f"Hilfe - {mode_name}")
    dialog.setMinimumSize(550, 500)

    dialog_layout = QVBoxLayout(dialog)
    text_browser = QTextBrowser(dialog)
    text_browser.setHtml(
        f"<div style='font-size:14px; line-height:1.4;'>{help_text}</div>"
    )
    dialog_layout.addWidget(text_browser)

    close_btn = QPushButton("Schließen", dialog)
    close_btn.clicked.connect(dialog.accept)
    dialog_layout.addWidget(close_btn)

    dialog.exec()


def create_setup_ui(game):
    from dart_cup import SPIEL_MODI

    widget = QWidget()
    content_layout = QVBoxLayout()
    content_layout.setSpacing(15)

    title_label = QLabel("Dart Setup")
    title_label.setStyleSheet(
        "font-size: 24px; font-weight: bold; color: #3daee9; margin-bottom: 10px;"
    )
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    content_layout.addWidget(title_label)

    # Zeile 1: Modus und Variante
    row1 = QHBoxLayout()
    row1.addWidget(QLabel("Spielmodus:"))
    game.mode_box = QComboBox()
    game.mode_box.addItems(list(SPIEL_MODI.keys()))
    row1.addWidget(game.mode_box)

    help_btn = QPushButton("?")
    help_btn.setFixedSize(25, 25)
    help_btn.setStyleSheet(
        "background-color: #34495e; font-weight: bold; border-radius: 12px;"
    )
    help_btn.clicked.connect(
        lambda: show_help_dialog(widget, game.mode_box.currentText())
    )
    row1.addWidget(help_btn)

    row1.addSpacing(20)
    row1.addWidget(QLabel("Variante:"))
    game.variant_box = QComboBox()
    row1.addWidget(game.variant_box)
    content_layout.addLayout(row1)

    # Die korrigierte Logik: Checkboxen bleiben sichtbar, werden aber de-/aktiviert
    def update_variant_box():
        mode = game.mode_box.currentText()
        game.variant_box.clear()
        if mode in SPIEL_MODI and SPIEL_MODI[mode][2] is not None:
            game.variant_box.addItems(SPIEL_MODI[mode][2])
            game.variant_box.setEnabled(True)
        else:
            game.variant_box.addItems(["Standard"])
            game.variant_box.setEnabled(False)

        if mode in SPIEL_MODI:
            is_x01 = SPIEL_MODI[mode][3]
            # Immer anzeigen (True), aber Aktivierung steuern
            game.cb_double_in.setEnabled(is_x01)
            game.cb_double_out.setEnabled(is_x01)
            game.lbl_double_in.setEnabled(is_x01)
            game.lbl_double_out.setEnabled(is_x01)

            if not is_x01:
                game.cb_double_in.setChecked(False)
                game.cb_double_out.setChecked(False)

    game.mode_box.currentTextChanged.connect(update_variant_box)

    # Zeile 2: Die Checkboxen (Jetzt dauerhaft im Layout)
    row2 = QHBoxLayout()
    game.lbl_double_in = QLabel("Double In:")
    row2.addWidget(game.lbl_double_in)
    game.cb_double_in = QCheckBox()
    row2.addWidget(game.cb_double_in)
    row2.addSpacing(20)

    game.lbl_double_out = QLabel("Double Out:")
    row2.addWidget(game.lbl_double_out)
    game.cb_double_out = QCheckBox()
    row2.addWidget(game.cb_double_out)
    row2.addSpacing(20)

    row2.addWidget(QLabel("Reihenfolge auslosen:"))
    game.cb_randomize = QCheckBox()
    row2.addWidget(game.cb_randomize)
    row2.addSpacing(20)

    row2.addWidget(QLabel("Bis zum Ende spielen:"))
    game.cb_play_to_end = QCheckBox()
    row2.addWidget(game.cb_play_to_end)

    row2.addStretch()
    content_layout.addLayout(row2)

    # Initialer Aufruf, damit der Zustand beim Start direkt passt
    update_variant_box()

    # Grid für die Spieler-Eingaben (Kompaktes 2-Spalten-Layout)
    grid_names = QGridLayout()
    grid_names.setVerticalSpacing(8)
    grid_names.setHorizontalSpacing(15)
    game.player_inputs = []
    game.bot_types = []
    BOT_OPTIONS = ["Mensch", "Dynamisch"] + [f"Level {i}" for i in range(1, 11)]

    for i in range(8):
        row = i % 4
        col_offset = 0 if i < 4 else 2

        lbl = QLabel(f"Spieler {i+1}:")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"Name {i+1}")

        bot_combo = QComboBox()
        bot_combo.addItems(BOT_OPTIONS)
        bot_combo.setFixedWidth(110)

        grid_names.addWidget(lbl, row, col_offset)
        grid_names.addWidget(line_edit, row, col_offset + 1)
        grid_names.addWidget(
            bot_combo, row, col_offset + 1, Qt.AlignmentFlag.AlignRight
        )

        line_edit.setStyleSheet("padding-right: 120px;")

        game.player_inputs.append(line_edit)
        game.bot_types.append(bot_combo)

    grid_names.setColumnStretch(0, 1)
    grid_names.setColumnStretch(1, 0)
    grid_names.setColumnStretch(2, 1)
    grid_names.setColumnStretch(3, 0)
    content_layout.addLayout(grid_names)

    main_center_layout = QHBoxLayout()
    main_center_layout.addStretch(1)
    main_center_layout.addLayout(content_layout, 10)
    main_center_layout.addStretch(1)

    # Untere Button-Leiste
    bottom = QHBoxLayout()
    bottom.setContentsMargins(10, 5, 10, 10)

    start_btn = QPushButton("GAME START")
    start_btn.setStyleSheet(
        "background-color: #27ae60; padding-left: 15px; padding-right: 15px; font-weight: bold; min-height: 32px;"
    )
    start_btn.clicked.connect(game.start_game)
    bottom.addWidget(start_btn)

    bottom.addStretch()
    game.stats_btn = QPushButton("Statistiken")
    game.stats_btn.setStyleSheet(
        "background-color: #34495e; padding-left: 15px; padding-right: 15px; min-height: 32px;"
    )
    bottom.addWidget(game.stats_btn)
    bottom.addSpacing(20)

    exit_btn = QPushButton("Programm beenden")
    exit_btn.setStyleSheet(
        "background-color: #96281b; padding-left: 15px; padding-right: 15px; min-height: 32px;"
    )
    exit_btn.clicked.connect(sys.exit)
    bottom.addWidget(exit_btn)

    main_layout = QVBoxLayout()
    main_layout.addLayout(main_center_layout, 1)
    main_layout.addLayout(bottom)

    widget.setLayout(main_layout)
    return widget
