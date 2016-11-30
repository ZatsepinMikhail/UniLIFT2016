import multiprocessing
import threading
import Queue


class MotionController:

    class StrategyModule:
        def __init__(self, button_handler_queue, motion_controller):
            self.priority_queue = Queue.PriorityQueue()
            self.button_handler_queue = button_handler_queue
            self.motion_controller = motion_controller

        # aim = [storey, inner-outer]
        def add_new_aim(self, new_aim):
            print 'insert new aim ', new_aim
            previous_first_aim = [-1, False]
            if not self.priority_queue.empty():
                previous_first_aim = self.priority_queue.queue[0]

            self.priority_queue.put(new_aim)

            # get min value from priority queue
            updated_first_aim = self.priority_queue.queue[0]
            if previous_first_aim != updated_first_aim:
                print 'notify motion controller', previous_first_aim, ' -> ', updated_first_aim
                self.motion_controller.event_new_aim.set()

            else:
                # print previous_first_aim, updated_first_aim
                pass

        def get_new_aim(self):
            self.motion_controller.event_new_aim.clear()
            return self.priority_queue.queue[0]

        def remove_aim(self, aim):
            pass

        def run(self):
            while True:
                new_aim = self.button_handler_queue.get()
                self.add_new_aim(new_aim)

    def __init__(self, button_handler_queue, weight_limit):
        self.event_new_aim = threading.Event()
        self.strategy_module = MotionController.StrategyModule(button_handler_queue, self)
        self.current_storey = 1
        self.current_aim = -1
        self.new_aim = -1
        self.weight_limit = weight_limit

    def get_current_storey(self):
        return self.current_storey

    def run_check_new_aim(self):
        while True:
            self.event_new_aim.wait()
            new_aim = self.strategy_module.get_new_aim()
            print 'Motion Controller: got new aim ', new_aim

    def run_engine(self):
        while True:
            while self.current_aim != -1:
                pass

    def run(self):
        thread_new_aim_checker = threading.Thread(target=self.run_check_new_aim)
        thread_engine = threading.Thread(target=self.run_engine())

        thread_new_aim_checker.start()


        self.strategy_module.run()

# solution to the problem of unpickable objects
def init_run(button_handler_queue, weight_limit):
    strategy_module_event = multiprocessing.Event()
    motion_controller = MotionController(button_handler_queue, weight_limit)
    motion_controller.run()
