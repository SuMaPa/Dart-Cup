import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QLabel, QPushButton, QHeaderView, QTabWidget, QComboBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ui.stats_viewer import DartStatsEngine

class StatsWindow(QWidget):
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window
        self.setWindowTitle("ProDartLeague - Statistiken & Analysen")
        self.resize(850, 500)
        self.engine = DartStatsEngine()
        center_point = self.screen().availableGeometry().center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        self.setStyleSheet("""
            QWidget {
                background-color: #1b1e20;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #3daee9;
                background-color: #232629;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #31363b;
                color: #b0b0b0;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #232629;
                color: #3daee9;
                font-weight: bold;
                border: 1px solid #3daee9;
                border-bottom-color: #232629;
                outline: none; /* Verhindert die Fokus-Unterstreichung */
            }
            QTableWidget {
                background-color: #232629;
                border: none;
                gridline-color: #31363b;
            }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected { background-color: #2a9cd6; color: white; }
            QHeaderView::section {
                background-color: #31363b;
                color: #3daee9;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #232629;
            }
            QComboBox {
                background-color: #31363b;
                border: 1px solid #3daee9;
                border-radius: 4px;
                padding: 5px;
                color: white;
                min-width: 150px;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                height: 35px;
            }
            QPushButton:hover { background-color: #415b76; }
        """)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        title = QLabel("PRO DART LEAGUE - STATISTIKEN")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #3daee9; letter-spacing: 1px; margin-bottom: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        self.tabs = QTabWidget()
        self.tabs.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Fokus-Linie komplett unterdrücken
        self.init_history_tab()
        self.init_player_tab()
        main_layout.addWidget(self.tabs)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        close_btn = QPushButton("Schließen")
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(self.close_and_restore)
        bottom_layout.addWidget(close_btn)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def init_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Datum", "Modus", "Gewinner", "Teilnehmer"])
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Match-Historie")
        self.load_history_data()

    def init_player_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Spieler auswählen:"))
        self.player_box = QComboBox()
        self.player_box.currentTextChanged.connect(self.update_player_stats)
        filter_layout.addWidget(self.player_box)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Metrik", "Wert"])
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.stats_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.stats_table)
        self.heatmap_label = QLabel("Lieblings-Segmente (Heatmap): -")
        self.heatmap_label.setStyleSheet("color: #fdbc4b; font-weight: bold; padding: 5px;")
        layout.addWidget(self.heatmap_label)
        widget.setLayout(layout)
        self.tabs.addTab(widget, "Spieler-Profile")
        all_players = self.engine.get_all_tracked_players()
        self.player_box.addItems(all_players)

    def load_history_data(self):
        matches = self.engine.load_all_matches()
        self.history_table.setRowCount(len(matches))

        for row, data in enumerate(matches):
            item_datum = QTableWidgetItem(data.get("datum", "Unbekannt"))
            item_modus = QTableWidgetItem(data.get("modus", "Unbekannt"))
            item_gewinner = QTableWidgetItem(data.get("gewinner", "Unbekannt"))
            item_gewinner.setForeground(QColor("#fdbc4b"))
            teilnehmer_liste = ", ".join(data.get("teilnehmer", []))
            item_teilnehmer = QTableWidgetItem(teilnehmer_liste)
            item_datum.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_modus.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_table.setItem(row, 0, item_datum)
            self.history_table.setItem(row, 1, item_modus)
            self.history_table.setItem(row, 2, item_gewinner)
            self.history_table.setItem(row, 3, item_teilnehmer)

    def update_player_stats(self, player_name):
        if not player_name:
            return
        stats = self.engine.calculate_player_profile(player_name)
        metriken = [
            ("Gespielte Matches", str(stats["matches_played"])),
            ("Gewonnene Spiele", str(stats["wins"])),
            ("Siegquote", f"{stats['win_rate']:.1f} %"),
            ("Geworfene Darts (Gesamt)", str(stats["total_darts"])),
            ("3-Dart-Average (Classic X01)", f"{stats['x01_avg']:.2f}" if stats["x01_avg"] > 0 else "N/A"),
            ("Meiste Aufnahmen (Highscore)", f"180er: {stats['180s']} | 140+: {stats['140s']} | 100+: {stats['100s']}")
        ]
        self.stats_table.setRowCount(len(metriken))
        for row, (metric, val) in enumerate(metriken):
            self.stats_table.setItem(row, 0, QTableWidgetItem(metric))
            self.stats_table.setItem(row, 1, QTableWidgetItem(val))
        top_fields = stats["top_segments"]
        if top_fields:
            text = "Lieblings-Segmente (Heatmap):   " + "   |   ".join([f"{k} ({v}x)" for k, v in top_fields])
        else:
            text = "Lieblings-Segmente (Heatmap): Noch keine Würfe dokumentiert."
        self.heatmap_label.setText(text)

    def close_and_restore(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.show()
        event.accept()
