import multiprocessing
import threading
import bisect


class MotionController:

    class StrategyModule:
        def __init__(self, button_handler_queue, motion_controller):

            #set of all aims
            self.all_aims = []

            self.button_handler_queue = button_handler_queue
            self.motion_controller = motion_controller

        def get_nearest_aim(self):

            items = self.all_aims
            nearest_aim = -1 if len(items) == 0 else items[0]
            for index in xrange(0, len(items) - 1):
                if items[index] <= self.motion_controller.current_storey <= items[index + 1]:
                    if self.motion_controller.current_speed <= 0:
                        nearest_aim = items[index]
                    elif self.motion_controller.current_speed > 0:
                        nearest_aim = items[index + 1]
                pass

            return nearest_aim


        # aim = [storey, inner-outer]
        def add_new_aim(self, new_aim):

            previous_first_aim = self.get_nearest_aim()

            bisect.insort_right(self.all_aims, new_aim)

            # get min value from priority queue
            updated_first_aim = self.get_nearest_aim()
            if previous_first_aim != updated_first_aim:
                print 'strategy_module: notify motion controller', previous_first_aim, ' -> ', updated_first_aim
                print list(self.all_aims)
                self.motion_controller.event_new_aim.set()

            else:
                # print previous_first_aim, updated_first_aim
                pass

        def get_new_aim(self):
            self.motion_controller.event_new_aim.clear()
            return self.get_nearest_aim()

        def remove_aim(self, aim):
            pass

        def run(self):
            while True:
                new_aim = self.button_handler_queue.get()
                print 'strategy_module: got new aim ', new_aim
                if new_aim[0] not in self.all_aims:
                    self.add_new_aim(new_aim[0])

    def __init__(self, button_handler_queue, weight_limit):
        self.event_new_aim = threading.Event()
        self.strategy_module = MotionController.StrategyModule(button_handler_queue, self)
        self.current_storey = 1

        #-1, 0, 1
        self.current_speed = 0
        self.current_aim = -1
        self.new_aim = -1
        self.weight_limit = weight_limit

    def get_current_storey(self):
        return self.current_storey

    def run_check_new_aim(self):
        while True:
            self.event_new_aim.wait()
            new_aim = self.strategy_module.get_new_aim()
            print 'motion_controller: got new aim ', new_aim

    def run_engine(self):
        while True:
            while self.current_aim != -1:
                pass

    def run(self):
        thread_new_aim_checker = threading.Thread(target=self.run_check_new_aim)
        #thread_engine = threading.Thread(target=self.run_engine())

        thread_new_aim_checker.start()
        self.strategy_module.run()

# solution to the problem of unpickable objects
def init_run(button_handler_queue, weight_limit):
    strategy_module_event = multiprocessing.Event()
    motion_controller = MotionController(button_handler_queue, weight_limit)
    motion_controller.run()
