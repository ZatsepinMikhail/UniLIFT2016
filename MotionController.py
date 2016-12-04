import threading
import bisect

from DoorController import *
from LightController import *
from WeightSensor import *
from Common import LiftState


class MotionController(object):

    class StrategyModule(object):

        def __init__(self, button_handler_queue, motion_controller):

            # list of all aims
            self.all_aims = []

            self.button_handler_queue = button_handler_queue
            self.motion_controller = motion_controller

        def get_nearest_aim(self):

            items = self.all_aims
            nearest_aim = -1 if len(items) == 0 else items[0]

            self.motion_controller.lock.acquire()
            current_storey = self.motion_controller.current_storey
            self.motion_controller.lock.release()
            # print("CURRENT STOREY: ", current_storey)

            for index in range(0, len(items) - 1):
                if items[index] <= current_storey <= items[index + 1]:
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
                print('strategy_module: notify motion controller', previous_first_aim, ' -> ', updated_first_aim)
                self.motion_controller.event_new_aim.set()

            else:
                # print previous_first_aim, updated_first_aim
                pass

        def get_new_aim(self):
            self.motion_controller.event_new_aim.clear()
            return self.get_nearest_aim()

        def remove_aim(self, aim):
            self.all_aims.remove(aim)
            pass

        def run(self):
            while True:
                new_aim = self.button_handler_queue.get()
                #print 'strategy_module: got new aim ', new_aim
                if new_aim[0] not in self.all_aims:
                    self.add_new_aim(new_aim[0])

    def __init__(self, button_handler_queue, weight_limit):
        self.event_new_aim = threading.Event()
        self.event_for_engine = threading.Event()
        self.strategy_module = MotionController.StrategyModule(button_handler_queue, self)
        self.current_storey = 1

        # -1, 0, 1
        self.current_speed = 0
        self.current_aim = -1
        self.new_aim = -1
        self.lock = threading.Lock()

        self.door_controller = DoorController()
        self.light_controller = LightController()
        self.weight_sensor = WeightSensor(weight_limit)

    def get_current_state(self):
        state = LiftState(
            self.get_current_storey(),
            self.door_controller.get_open_state(),
            self.light_controller.get_light_state(),
            self.weight_sensor.get_weight())
        return state

    def get_current_storey(self):
        return self.current_storey

    def run_check_new_aim(self):
        while True:
            self.event_new_aim.wait()
            self.new_aim = self.strategy_module.get_new_aim()
            print('motion_controller: got new aim ', self.new_aim)
            self.event_for_engine.set()

    def run_engine(self):
        while True:
            if self.current_speed == 0:
                self.event_for_engine.wait()

                # bad decision
                self.event_for_engine.clear()
                self.current_aim = self.new_aim

                if self.current_aim > self.current_storey:
                    self.current_speed = 1
                elif self.current_aim < self.current_storey:
                    self.current_speed = -1

            elif self.event_for_engine.is_set():
                print('engine: change aim ' + str(self.current_aim) + ' -> ' + str(self.new_aim))
                self.current_aim = self.new_aim
                if self.current_aim > self.current_storey:
                    self.current_speed = 1
                elif self.current_aim < self.current_storey:
                    self.current_speed = -1

            time.sleep(1)

            self.lock.acquire()
            self.current_storey += self.current_speed
            print('engine: current_storey ', self.current_storey)
            if self.current_storey == self.current_aim:
                self.current_speed = 0
                self.light_controller.turn_light_on()
                while True:
                    self.door_controller.release_passengers(self.weight_sensor)
                    if self.weight_sensor.is_limit_exceeded():
                        continue
                    if self.weight_sensor.is_empty():
                        self.light_controller.turn_light_off()
                    break
                self.strategy_module.remove_aim(self.current_aim)
            self.lock.release()

    def run(self):
        thread_new_aim_checker = threading.Thread(target=self.run_check_new_aim)
        thread_engine = threading.Thread(target=self.run_engine)

        thread_new_aim_checker.start()
        thread_engine.start()
        self.strategy_module.run()


# solution to the problem of unpickable objects
def init_run(button_handler_queue, weight_limit):
    motion_controller = MotionController(button_handler_queue, weight_limit)
    motion_controller.run()
