import sys
from PyQt6.QtWidgets import QApplication
import spiel.clock as clock
import spiel.classic as classic
import spiel.cricket as cricket
import spiel.killer as killer
import spiel.shanghai as shanghai
import spiel.halve_it as halve_it
import spiel.bob as bob
from logs.log import logger


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Ungefangener Fehler", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception

SPIEL_MODI = {
    # "Name": (Prozess_Fn, Init_Fn, Varianten pulldown, double in/out, ui_verhalten)
    "Bob's 27": (bob.spiel_bobs27, bob.init_bobs27, False, False, "standard"),
    "Classic X01": (classic.process_classic, classic.init_classic, True, True, "standard"),
    "Elimination": (classic.process_classic, classic.init_classic, True, True, "collision_detection"),
    "Mensch-ärgere-dich-nicht!": (classic.process_classic, classic.init_classic, True, True, "collision_detection"),
    "Cricket": (cricket.process_cricket, cricket.init_cricket, True, False, "standard"),
    "Around the Clock": (clock.process_around_the_clock, clock.init_around_the_clock, False, False, "target_scoring"),
    "Around the Clock (Plus)": (clock.process_around_the_clock_extreme, clock.init_around_the_clock, False, False, "target_scoring"),
    "Shanghai": (shanghai.process_shanghai, shanghai.init_shanghai, False, False, "standard"),
    "Halve It": (halve_it.process_halve_it, halve_it.init_halve_it, False, False, "standard"),
    "Killer": (killer.process_killer, killer.init_killer, False, False, "life_tracking")
}

PUNKTE_VARIANTEN = ["101", "301", "501", "701", "901"]

if __name__ == '__main__':
    from ui.main_window import ProDartLeague
    app = QApplication(sys.argv)
    ex = ProDartLeague()
    ex.setWindowTitle("Dart Cup v.22.05.26")
    ex.show()
    sys.exit(app.exec())
