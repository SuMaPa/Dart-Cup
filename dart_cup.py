import sys
from logs.log import logger
from PyQt6.QtWidgets import QApplication
import spiel.clock as clock
import spiel.classic as classic
import spiel.elimination as elimination
import spiel.mensch as mensch
import spiel.cricket as cricket
import spiel.killer as killer
import spiel.shanghai as shanghai
import spiel.halve_it as halve_it
import spiel.bob as bob


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Ungefangener Fehler", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception

SPIEL_MODI = {
    # "Name": (Prozess_Fn, Init_Fn, Varianten_Liste, double in/out checkbox, ui_verhalten)
    "Bob's 27": (bob.spiel_bobs27, bob.init_bobs27, ["Classic", "Einsteiger", "Open End"], False, "standard"),
    "Classic X01": (classic.process_classic, classic.init_classic, ["101", "301", "501", "701", "901"], True, "standard"),
    "Elimination": (elimination.process_elimination, elimination.init_elimination, ["301", "501", "701"], True, "collision_detection"),
    "Mensch-ärgere-dich-nicht!": (mensch.process_mensch, mensch.init_mensch, ["301", "501", "701"], True, "collision_detection"),
    "Cricket": (cricket.process_cricket, cricket.init_cricket, ["Standard", "Cut-Throat", "No-Score"], False, "standard"),
    "Around the Clock": (clock.process_around_the_clock, clock.init_around_the_clock, ["Standard", "Double-Only", "All-In"], False, "target_scoring"),
    "Shanghai": (shanghai.process_shanghai, shanghai.init_shanghai, ["Standard", "Double-Only", "Shanghai-Finish"], False, "target_scoring"),
    "Halve It": (halve_it.process_halve_it, halve_it.init_halve_it, ["Standard", "Kurz", "Pro Challenge"], False, "standard"),
    "Killer": (killer.process_killer, killer.init_killer, ["Standard", "Direkt-Killer", "Totaler Krieg"], False, "life_tracking")
}

if __name__ == '__main__':
    from ui.main_window import ProDartLeague
    app = QApplication(sys.argv)
    ex = ProDartLeague()
    ex.setWindowTitle("Dart Cup v.01.06.26")
    ex.show()
    sys.exit(app.exec())
