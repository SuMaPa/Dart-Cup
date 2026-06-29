# ui/keyboard_handler.py
from PyQt6.QtCore import Qt, QTimer


def handle_key_press(ui, event):
    if ui.stack.currentIndex() != 1 or not ui.btn_double.isEnabled():
        return

    key = event.key()
    if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
        temp_input = ui.typed_score + chr(key)
        if int(temp_input) <= 20 or int(temp_input) in (25, 50):
            ui.typed_score = temp_input
            update_keyboard_feedback(ui)
        else:
            ui.score_label.setText("LIMIT")
            ui.score_label.setStyleSheet(
                "font-size: 90px; font-weight: bold; color: #ff4c4c;"
            )
            QTimer.singleShot(500, ui.update_display)
            ui.typed_score = ""

    elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
        if ui.typed_score:
            val = int(ui.typed_score)
            if val == 50:
                ui.modifier = 2
                ui.num_clicked(25)
            else:
                ui.num_clicked(val)
            ui.typed_score = ""
            ui.update_display()

    elif key == Qt.Key.Key_Backspace:
        if ui.typed_score:
            ui.typed_score = ui.typed_score[:-1]
            if not ui.typed_score:
                ui.update_display()
            else:
                update_keyboard_feedback(ui)
        else:
            ui.undo_hit()

    elif key == Qt.Key.Key_D:
        ui.btn_double.click()
    elif key == Qt.Key.Key_T:
        ui.btn_triple.click()


def update_keyboard_feedback(ui):
    if ui.typed_score:
        ui.score_label.setText(ui.typed_score)
        ui.score_label.setStyleSheet(
            "font-size: 90px; font-weight: bold; color: #fdbc4b;"
        )
    else:
        ui.update_display()
