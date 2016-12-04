import multiprocessing, threading
import Buttons
import ButtonHandler
import MotionController

import random, time
from time import sleep
from PyQt5.QtWidgets import QMainWindow, QFrame
from PyQt5.QtGui import QPainter, QColor


class Lift(QMainWindow):

    def __init__(self):
        super().__init__()

        self.init_processes()
        self.init_ui()
        process_state = threading.Thread(target=self.update_state)
        process_state.start()
        # self.update_state()

    def init_processes(self):
        # queue buttons - button_handler
        queue_buttons_bh = multiprocessing.Queue()

        # queue button_handler - strategy_module
        queue_bh_sm = multiprocessing.Queue()

        num_storey = 10
        weight_limit = 100

        button_handler = ButtonHandler.ButtonHandler(queue_buttons_bh, queue_bh_sm)
        self.motion_controller = MotionController.MotionController(queue_bh_sm, weight_limit)

        process_buttons = multiprocessing.Process(target=Buttons.simulate_buttons_pressure,
                                                  args=(num_storey, queue_buttons_bh))
        process_button_handler = multiprocessing.Process(target=button_handler.run)

        process_motion_controller = multiprocessing.Process(target=self.motion_controller.run)

        process_buttons.start()
        process_button_handler.start()
        process_motion_controller.start()

        # time.sleep(10)
        #
        # process_buttons.join()
        # process_button_handler.join()
        # process_motion_controller.join()
        #
        # queue_buttons_bh.close()
        # queue_bh_sm.close()

        # process_state = multiprocessing.Process(target=self.update_state)
        # process_state.run()

    def init_ui(self):

        self.tboard = Board(self)
        self.setCentralWidget(self.tboard)

        # self.statusbar = self.statusBar()
        # self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)
        #
        # self.tboard.start()

        self.resize(300, 400)
        self.setWindowTitle('Lift')
        self.show()

    def update_state(self):
        while True:
            sleep(1)
            current_storey = self.motion_controller.current_storey.value
            self.tboard.set_state(current_storey)
            # print("CURRENT ", current_storey)
            # self.update()




class StoreyState:
    Empty = 0
    Lift = 1



class Board(QFrame):

    BoardWidth = 2
    BoardHeight = 11

    def __init__(self, parent):
        super().__init__(parent)

        self.current_storey = 1
        # self.current_storey = multiprocessing.Value("i", 1)

    def set_state(self, current_storey):
        self.current_storey = current_storey
        self.update()
        # self.paintEvent(None)
        print("board: set state ", self.current_storey)

    def square_width(self):
        return self.contentsRect().width() // Board.BoardWidth

    def square_height(self):
        return self.contentsRect().height() // Board.BoardHeight

    def state_at(self, storey):
        if storey == self.current_storey:
            return StoreyState.Lift
        else:
            return StoreyState.Empty

    def paintEvent(self, event):
        print("PAINT")
        painter = QPainter(self)
        rect = self.contentsRect()

        boardTop = rect.bottom() - Board.BoardHeight * self.square_height()

        for i in range(Board.BoardHeight):
            self.drawSquare(painter, rect.left(), boardTop + i * self.square_height(), self.state_at(i))

        # self.set_state(self.current_storey + 1)

    def drawSquare(self, painter, x, y, shape):

        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

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
