import multiprocessing
import Buttons
import ButtonHandler
import MotionController
import Lift

import time, sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':

    # # queue buttons - button_handler
    # queue_buttons_bh = multiprocessing.Queue()
    #
    # # queue button_handler - strategy_module
    # queue_bh_sm = multiprocessing.Queue()
    # num_storey = 10
    #
    # button_handler = ButtonHandler.ButtonHandler(queue_buttons_bh, queue_bh_sm)
    #
    # process_buttons = multiprocessing.Process(target=Buttons.simulate_buttons_pressure,
    #                                           args=(num_storey, queue_buttons_bh))
    # process_button_handler = multiprocessing.Process(target=button_handler.run)
    #
    # process_motion_controller = multiprocessing.Process(target=MotionController.init_run,
    #                                                     args=(queue_bh_sm, 100))
    #
    # process_buttons.start()
    # process_button_handler.start()
    # process_motion_controller.start()
    #
    # time.sleep(100)
    #
    # process_buttons.join()
    # process_button_handler.join()
    # process_motion_controller.join()
    #
    # queue_buttons_bh.close()
    # queue_bh_sm.close()

    app = QApplication([])
    lift = Lift.Lift()
    sys.exit(app.exec_())
