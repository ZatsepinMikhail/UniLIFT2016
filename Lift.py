import multiprocessing
import threading
import Buttons
import ButtonHandler
import MotionController
import LiftGUI
import Common

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
        queue_buttons_bh = multiprocessing.Queue()

        # queue button_handler - strategy_module
        queue_bh_sm = multiprocessing.Queue()

        button_handler = ButtonHandler.ButtonHandler(queue_buttons_bh, queue_bh_sm)
        self.motion_controller = MotionController.MotionController(queue_bh_sm, self.weight_limit)

        self.buttons = Buttons.Buttons(self.num_storey, queue_buttons_bh)
        # process_buttons = multiprocessing.Process(target=Buttons.simulate_buttons_pressure,
        #                                           args=(self.num_storey, queue_buttons_bh))
        process_button_handler = multiprocessing.Process(target=button_handler.run)

        process_motion_controller = threading.Thread(target=self.motion_controller.run)

        # process_buttons.start()
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

    def init_ui(self):

        self.tboard = LiftGUI.LiftGUI(self, self.num_storey)
        self.setCentralWidget(self.tboard)

        self.resize(300, 400)
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





