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

    is_inner_button_pressed = False

    def __init__(self):
        super().__init__()

        self.num_storey = 9
        self.weight_limit = 200

        self.init_processes()
        self.init_ui()
        self.process_state = threading.Thread(target=self.update_state)
        self.process_state.start()

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

        self.buttons = {False: {}, True: {}}
        for storey in range(1, self.num_storey + 1):
            for is_inner in (False, True):
                self.buttons[is_inner][storey] = Buttons.Button(storey, is_inner, self.queue_buttons_bh)

        self.process_button_handler = multiprocessing.Process(target=self.button_handler.run)

        self.process_motion_controller = threading.Thread(target=self.motion_controller.run)

        self.process_information_table = multiprocessing.Process(target=self.information_table.run)

        # process_buttons.start()
        self.process_button_handler.start()
        self.process_motion_controller.start()
        self.process_information_table.start()

    def init_ui(self):
        self.tboard = LiftGUI.LiftGUI(self, self.num_storey)
        self.setCentralWidget(self.tboard)

        self.resize(150, 400)
        self.setWindowTitle('Lift')
        self.show()

    def stop_work(self):
        # put poison pills
        self.queue_mc_ib.put('Q')
        self.queue_bh_sm.put('Q')
        self.queue_buttons_bh.put('Q')

        self.process_information_table.join()
        print('info table stopped')

        self.process_button_handler.join()
        print('button handler stopped')

        self.process_motion_controller.join()
        print('motion controller stopped')

        self.queue_mc_ib.close()
        self.queue_bh_sm.close()
        self.queue_buttons_bh.close()

    def update_state(self):
        while True:
            sleep(0.1)
            current_state = self.motion_controller.get_current_state()

            # poison pill
            if current_state.storey == 'Q':
                break
            self.tboard.set_state(current_state)
            # print("CURRENT ", current_state.storey)

    def keyPressEvent(self, event):
        key = event.key()

        if key >= Qt.Key_1 and key <= Qt.Key_9:
            self.buttons[self.is_inner_button_pressed][key - Qt.Key_1 + 1].press()
        elif key == Qt.Key_Alt:
            self.is_inner_button_pressed = True
        elif key == Qt.Key_Q:
            self.stop_work()
        else:
            super(Lift, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        key = event.key()

        if key == Qt.Key_Alt:
            self.is_inner_button_pressed = False