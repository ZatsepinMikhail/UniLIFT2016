import multiprocessing
import threading
import Buttons
import ButtonHandler
import MotionController
import LiftGUI
import InformationBoard

from time import sleep
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt


class Lift(QMainWindow):

    def __init__(self):
        super().__init__()

        self.num_storey = 9
        self.weight_limit = 100

        self.init_processes()
        self.init_ui()
        process_state = threading.Thread(target=self.update_state)
        process_state.start()

    def init_processes(self):
        # queue buttons - button_handler
        self.queue_buttons_bh = multiprocessing.Queue()

        # queue button_handler - strategy_module
        self.queue_bh_sm = multiprocessing.Queue()

        # queue motion_controller - information_board
        self.queue_mc_ib = multiprocessing.Queue()

        self.button_handler = ButtonHandler.ButtonHandler(self.queue_buttons_bh, self.queue_bh_sm)
        self.motion_controller = MotionController.MotionController(self.queue_bh_sm, self.queue_mc_ib, self.weight_limit)
        self.information_table = InformationBoard.InformationBoard(self.queue_mc_ib)

        self.buttons = Buttons.Buttons(self.num_storey, self.queue_buttons_bh)
        # process_buttons = multiprocessing.Process(target=Buttons.simulate_buttons_pressure,
        #                                           args=(self.num_storey, queue_buttons_bh))
        self.process_button_handler = multiprocessing.Process(target=self.button_handler.run)

        self.process_motion_controller = threading.Thread(target=self.motion_controller.run)

        self.process_information_table = multiprocessing.Process(target=self.information_table.run)

        # process_buttons.start()
        self.process_button_handler.start()
        self.process_motion_controller.start()
        self.process_information_table.start()

    def __del__(self):
        # should be corrected
        print(u"Вызван метод __del__()")
        self.process_button_handler.join()
        self.process_motion_controller.join()

        self.queue_buttons_bh.close()
        self.queue_bh_sm.close()

    def init_ui(self):
        self.tboard = LiftGUI.LiftGUI(self, self.num_storey)
        self.setCentralWidget(self.tboard)

        self.resize(150, 400)
        self.setWindowTitle('Lift')
        self.show()

    def update_state(self):
        while True:
            sleep(0.1)
            current_state = self.motion_controller.get_current_state()
            self.tboard.set_state(current_state)
            # print("CURRENT ", current_state.storey)

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_1:
            self.buttons.press(1)
        elif key == Qt.Key_2:
            self.buttons.press(2)
        elif key == Qt.Key_3:
            self.buttons.press(3)
        elif key == Qt.Key_4:
            self.buttons.press(4)
        elif key == Qt.Key_5:
            self.buttons.press(5)
        elif key == Qt.Key_6:
            self.buttons.press(6)
        elif key == Qt.Key_7:
            self.buttons.press(7)
        elif key == Qt.Key_8:
            self.buttons.press(8)
        elif key == Qt.Key_9:
            self.buttons.press(9)
        else:
            super(Lift, self).keyPressEvent(event)
