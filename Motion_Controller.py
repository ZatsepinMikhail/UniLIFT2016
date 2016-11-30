import Strategy_Module
import multiprocessing
from threading import Thread

class MotionController:

    def __init__(self, strategy_module, weight_limit):
        self.strategy_module = strategy_module
        self.current_storey = 1
        self.weight_limit = weight_limit
        self.strategy_module_event = self.strategy_module.strategy_module_event

    def get_current_storey(self):
        return self.current_storey

    def run_check_new_aim(self):
        while True:
            self.strategy_module_event.wait()
            new_aim = self.strategy_module.get_new_aim()
            print 'Motion Controller: got new aim ', new_aim

    def run_strategy_module(self):
        pass

    def run(self):
        #thread_strategy_module = Thread(target=self.strategy_module.run)
        thread_new_aim_checker = Thread(target=self.run_check_new_aim)
        thread_new_aim_checker.start()
        self.strategy_module.run()

# solution to the problem of unpickable objects
def init_run(button_handler_queue, weight_limit):
    strategy_module_event = multiprocessing.Event()
    strategy_module = Strategy_Module.StrategyModule(button_handler_queue, strategy_module_event)
    motion_controller = MotionController(strategy_module, weight_limit)
    motion_controller.run()
