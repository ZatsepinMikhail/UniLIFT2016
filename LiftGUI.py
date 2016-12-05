from Common import LiftState

from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRect


class StoreyState:
    EMPTY = 0
    LIFT_LIGHT = 1
    LIFT_DARK = 2


class LiftGUI(QFrame):

    storey_number_width = 30

    def __init__(self, parent, num_storey):
        super().__init__(parent)

        self.current_state = LiftState(1, False, False, 0)
        self.num_storey = num_storey

    def set_state(self, current_state):
        self.current_state = current_state
        self.update()

    def square_width(self):
        return self.contentsRect().width()

    def square_height(self):
        return self.contentsRect().height() // self.num_storey

    def state_at(self, storey):
        if storey == self.current_state.storey:
            if self.current_state.is_light:
                return StoreyState.LIFT_LIGHT
            else:
                return StoreyState.LIFT_DARK
        else:
            return StoreyState.EMPTY

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.contentsRect()

        board_bottom = rect.bottom()

        for i in range(1, self.num_storey + 1):
            storey_top = board_bottom - i * self.square_height()
            self.draw_storey(painter, rect.left() + self.storey_number_width, storey_top, self.state_at(i))
            self.draw_storey_number(painter, rect.left(), storey_top, i)

    def draw_storey_number(self, painter, x, y, storey_number):
        rect = QRect(x + 1, y + 1, self.storey_number_width - 3, self.square_height() - 1)
        painter.fillRect(rect, Qt.gray)
        painter.setPen(Qt.black)
        painter.drawText(
            rect,
            Qt.AlignCenter,
            str(storey_number))

    def draw_storey(self, painter, x, y, storey_state):
        color_table = [Qt.black, Qt.yellow, Qt.blue]
        color = QColor(color_table[storey_state])

        painter.fillRect(x + 1, y + 1, self.square_width() - 2,
                         self.square_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.square_height() - 1, x, y)
        painter.drawLine(x, y, x + self.square_width() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.square_height() - 1,
                         x + self.square_width() - 1, y + self.square_height() - 1)
        painter.drawLine(x + self.square_width() - 1,
                         y + self.square_height() - 1, x + self.square_width() - 1, y + 1)

        if storey_state != StoreyState.EMPTY:
            if not self.current_state.is_open:
                painter.setBrush(QBrush(Qt.DiagCrossPattern))
                painter.drawRect(x + 1, y + 1, self.square_width() - 2, self.square_height() - 2)

            if self.current_state.weight > 0:
                painter.setPen(Qt.red)
                painter.drawText(
                    QRect(x + 1, y + 1, self.square_width() - 2, self.square_height() - 2),
                    Qt.AlignCenter,
                    str(self.current_state.weight))
