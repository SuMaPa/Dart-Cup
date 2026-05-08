# Dart-Cup 🎯

Ein schlankes und intuitives Dart-Scoreboard. Ursprünglich für Debian (KDE Plasma) konzipiert, läuft es dank Python und PyQt6 auf nahezu jedem modernen Betriebssystem.

## Features
*   **Vielseitige Spielmodi:** 301, 501, 701, Around the Clock und der berüchtigte **Elimination-Modus**.
*   **Regelwerk:** Optionale Unterstützung für Double In und Double Out.
*   **Multiplayer:** Bis zu 8 Spieler gleichzeitig.
*   **Intelligentes Scoreboard:** Automatische Platzierung, Highlight des Führenden und Erkennung von "Busts".
*   **Interaktive Hilfe:** Kleines Info-Icon im Setup mit Tooltips zu den einzelnen Spielvarianten.
*   **Undo-Funktion:** Ein Fehlwurf? Kein Problem, mit dem Undo-Button korrigierst du den letzten Pfeil.
*   **Konsequentes Ende:** Sobald das Spiel vorbei ist, wechselt der Abbruch-Button zu "Beenden" – für einen sauberen Abschluss.

## Voraussetzungen
*   **Python 3.8 oder höher:** Das Herzstück des Programms.
*   **PyQt6:** Das Framework für die grafische Benutzeroberfläche.

## Installation & Start

### 1. Abhängigkeiten installieren
Unter **Debian/Ubuntu**:
```bash
sudo apt update
sudo apt install python3-pyqt6

starten:
Datei downloaden und im Ordner dart_counter.py ausführen
