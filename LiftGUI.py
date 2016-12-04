from Common import LiftState

from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QPainter, QColor


class StoreyState:
    EMPTY = 0
    LIFT_LIGHT = 1
    LIFT_DARK = 2


class LiftGUI(QFrame):

    BoardWidth = 2

    def __init__(self, parent, num_storey):
        super().__init__(parent)

        self.current_state = LiftState(1, False, False, 0)
        self.num_storey = num_storey
        # self.current_storey = multiprocessing.Value("i", 1)

    def set_state(self, current_state):
        self.current_state = current_state
        self.update()
        # self.paintEvent(None)
        # print("board: set state ", self.current_storey)

    def square_width(self):
        return self.contentsRect().width() // LiftGUI.BoardWidth

    def square_height(self):
        return self.contentsRect().height() // (self.num_storey)

    def state_at(self, storey):
        if storey == self.current_state.storey:
            if self.current_state.is_light:
                return StoreyState.LIFT_LIGHT
            else:
                return StoreyState.LIFT_DARK
        else:
            return StoreyState.EMPTY

    def paintEvent(self, event):
        # print("PAINT")
        painter = QPainter(self)
        rect = self.contentsRect()

        board_bottom = rect.bottom()

        for i in range(1, self.num_storey + 1):
            self.drawSquare(painter, rect.left(), board_bottom - i * self.square_height(), self.state_at(i))

        # self.set_state(self.current_storey + 1)

    def drawSquare(self, painter, x, y, shape):

        # colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
        #               0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
        colorTable = [0x000000, 0xDAAA00, 0x0000FF]

        color = QColor(colorTable[shape])
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