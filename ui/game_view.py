from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QTableWidget,
    QHeaderView,
)
from PyQt6.QtCore import Qt


def create_game_ui(game):
    widget = QWidget()
    layout = QHBoxLayout()
    left = QVBoxLayout()

    # NEU: Ein horizontaler Info-Balken ganz oben, der die Punkte-Anzeige nicht verschiebt
    top_info_layout = QHBoxLayout()

    game.mode_info_label = QLabel("Game: -")
    game.mode_info_label.setStyleSheet(
        "font-size: 14px; color: #3daee9; font-weight: bold;"
    )
    top_info_layout.addWidget(game.mode_info_label)

    top_info_layout.addStretch(
        1
    )  # Schiebt die Rundenanzeige an den rechten Rand der linken Spalte

    game.round_info_label = QLabel("Runde: 1")
    game.round_info_label.setStyleSheet(
        "font-size: 14px; color: #fdbc4b; font-weight: bold;"
    )
    top_info_layout.addWidget(game.round_info_label)

    left.addLayout(top_info_layout)

    # Das alte game.info_label wird ersetzt. Der Rest bleibt absolut ORIGINAL.
    game.score_label = QLabel("301")
    game.score_label.setStyleSheet(
        "font-size: 90px; font-weight: bold; color: #3daee9;"
    )
    game.dart_label = QLabel("Darts: ○ ○ ○")
    left.addWidget(game.score_label)
    left.addWidget(game.dart_label)

    mod_layout = QHBoxLayout()
    game.btn_double = QPushButton("DOUBLE (D)")
    game.btn_triple = QPushButton("TRIPLE (T)")
    for b in [game.btn_double, game.btn_triple]:
        b.setCheckable(True)
        b.setStyleSheet(
            "QPushButton:checked { background-color: #27ae60; border: 1px solid white; }"
        )
        b.clicked.connect(game.mod_clicked)
        mod_layout.addWidget(b)
        game.num_buttons.append(b)
    left.addLayout(mod_layout)

    grid = QGridLayout()
    for i in range(1, 21):
        btn = QPushButton(str(i))
        btn.setFixedSize(60, 50)
        btn.clicked.connect(lambda ch, v=i: game.num_clicked(v))
        grid.addWidget(btn, (i - 1) // 5, (i - 1) % 5)
        game.num_buttons.append(btn)
    left.addLayout(grid)

    spec = QHBoxLayout()
    btn_miss = QPushButton("Miss")
    btn_miss.setStyleSheet(
        "background-color: #5d6368; height: 50px; font-weight: bold;"
    )
    btn_miss.clicked.connect(lambda: game.num_clicked(0))

    btn_25 = QPushButton("BULL")
    btn_25.setStyleSheet("background-color: #454a4f; height: 50px; font-weight: bold;")
    btn_25.clicked.connect(lambda: game.num_clicked(25))

    btn_bullseye = QPushButton("BULLSEYE")
    btn_bullseye.setStyleSheet(
        "background-color: #454a4f; height: 50px; font-weight: bold;"
    )
    btn_bullseye.clicked.connect(game.hit_bullseye)

    spec.addWidget(btn_miss)
    spec.addWidget(btn_25)
    spec.addWidget(btn_bullseye)
    game.num_buttons.extend([btn_miss, btn_25, btn_bullseye])
    left.addLayout(spec)

    ctrl = QHBoxLayout()
    game.undo_btn = QPushButton("Korrektur (Back)")  # game. hinzugefügt
    game.undo_btn.setStyleSheet(
        "QPushButton { background-color: #fdbc4b; color: black; font-weight: bold; height: 35px; } QPushButton:disabled { background-color: #554422; color: #888888; }"
    )
    game.undo_btn.clicked.connect(game.undo_hit)

    game.nochmal_btn = QPushButton("nochmal")
    game.nochmal_btn.setStyleSheet(
        "background-color: #3daee9; color: black; font-weight: bold; height: 35px;"
    )
    game.nochmal_btn.setVisible(False)  # Verstecken beim Start
    game.nochmal_btn.clicked.connect(game.start_game)

    game.back_btn = QPushButton("Abbrechen")
    game.back_btn.setStyleSheet("background-color: #454a4f; height: 35px;")
    game.back_btn.clicked.connect(game.cancel_game)

    ctrl.addWidget(game.undo_btn)
    ctrl.addWidget(game.nochmal_btn)
    ctrl.addWidget(game.back_btn)
    game.num_buttons.extend([game.undo_btn])
    left.addLayout(ctrl)

    # Flexibler Container für die rechte Seite
    game.right_layout = QVBoxLayout()

    # Das Standard-Layout (z.B. für Classic X01)
    game.table = QTableWidget()
    game.table.setColumnCount(3)
    game.table.setHorizontalHeaderLabels(["Spieler", "Letzte Würfe", "Score"])
    game.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    game.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    game.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    game.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    # Standard-Tabelle in den Container packen
    game.right_layout.addWidget(game.table)

    # Container in das Hauptlayout integrieren
    layout.addLayout(left, 3)
    layout.addLayout(game.right_layout, 4)

    widget.setLayout(layout)
    return widget
