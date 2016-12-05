import threading
import time
from OrderedSet import OrderedSet
import heapq

from DoorController import *
from LightController import *
from WeightSensor import *
from Common import LiftState


class MotionController(object):

    class StrategyModule(object):

        def __init__(self, button_handler_queue, motion_controller):

            # set of incoming aims
            self.aim_set = OrderedSet()
            self.aims_intermediate = []  # heap of intermediate aims
            self.aim_main = None
            self.is_main_finished = False
            # aim from the passengers inside the lift
            self.aim_internal = None

            self.button_handler_queue = button_handler_queue
            self.motion_controller = motion_controller

        def get_nearest_aim(self):
            with self.motion_controller.lock:
                assert len(self.aim_set) != 0 or self.aim_main is not None, 'Function cannot be called if there ' \
                                                                            ' are no new aims'
                if self.aim_main is not None:
                    # lock due to aims_intermediate
                    if not self.aims_intermediate:
                        res = self.aim_main
                    else:
                        while self.aims_intermediate and not self.is_intermediate_aim(self.aims_intermediate[0][0]):
                            heapq.heappop(self.aims_intermediate)
                        res = self.aims_intermediate[0] if self.aims_intermediate else self.aim_main
                else:
                    # define new main aim
                    if self.aim_internal is not None:
                        self.aim_main = self.aim_internal
                    else:
                        self.aim_main = next(x for x in self.aim_set)
                    # update intermediate aims
                    for aim in self.aim_set:
                        if self.is_intermediate_aim(aim[0]):
                            heapq.heappush(self.aims_intermediate, aim)
                    res = self.aim_main
            return res

        def is_intermediate_aim(self, storey_check, storey_from=None, storey_to=None):
            if storey_to is None:
                storey_to = self.aim_main[0]
            if storey_from is None:
                with self.motion_controller.lock:
                    storey_from = self.motion_controller.current_storey
            return max(storey_from, storey_to) - 1 >= storey_check >= min(storey_from, storey_to) + 1

        # aim = (storey, inner-outer)
        def add_new_aim(self, new_aim):
            with self.motion_controller.lock:
                # poison pill
                if new_aim == 'Q':
                    self.aim_main = 'Q'
                    self.motion_controller.event_new_aim.set()

                elif self.aim_main is not None:
                    # check if such an aim exists in set
                    if new_aim not in self.aim_set:
                        # add new_aim to the set
                        self.aim_set.add(new_aim)

                        # update heap of intermediate aims
                        if self.is_intermediate_aim(new_aim[0]):
                            heapq.heappush(self.aims_intermediate, new_aim)
                            self.motion_controller.event_new_aim.set()
                else:
                    if not self.aim_set:
                        self.aim_set.add(new_aim)
                        self.motion_controller.event_new_aim.set()
                    else:
                        self.aim_set.add(new_aim)
                    if self.is_main_finished and new_aim[1]:
                        # internal aim
                        self.aim_internal = new_aim

        def get_new_aim(self):
            self.motion_controller.event_new_aim.clear()
            if self.aim_main == 'Q':
                return self.aim_main
            else:
                return self.get_nearest_aim()

        def remove_aim(self, aim):
            with self.motion_controller.lock:
                self.aim_set.remove(aim)
                self.is_main_finished = False
                if self.aim_main == aim:
                    self.aim_main = None
                    self.is_main_finished = True
                if self.aims_intermediate and self.aims_intermediate[0] == aim:
                    heapq.heappop(self.aims_intermediate)
                if self.aim_internal == aim:
                    self.aim_internal = None
                if self.aim_set:
                    self.motion_controller.event_new_aim.set()

        def run(self):
            while True:
                new_aim = self.button_handler_queue.get()
                self.add_new_aim(new_aim)

                # poison pill
                if new_aim == 'Q':
                    break

                print('strategy_module: got new aim ' + str(new_aim))

    def __init__(self, button_handler_queue, information_board_queue, weight_limit):
        self.event_new_aim = threading.Event()
        self.event_for_engine = threading.Event()
        self.strategy_module = MotionController.StrategyModule(button_handler_queue, self)

        self.information_board_queue = information_board_queue
        self.current_storey = 1

        # -1, 0, 1
        self.current_speed = 0
        self.current_aim = None
        self.current_aim_storey = None
        self.new_aim = None
        self.lock = threading.RLock()

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
        with self.lock:
            res = self.current_storey
        return res

    def update_speed(self):
        with self.lock:
            current_storey = self.current_storey
        if self.current_aim_storey > current_storey:
            self.current_speed = 1
        elif self.current_aim_storey < current_storey:
            self.current_speed = -1
        else:
            self.current_speed = 0

    def run_check_new_aim(self):
        while True:
            self.event_new_aim.wait()
            with self.lock:
                self.new_aim = self.strategy_module.get_new_aim()

            self.event_for_engine.set()

            if self.new_aim == 'Q':
                break

    def run_engine(self):
        while True:

            if self.current_speed == 0 or self.event_for_engine.is_set():
                if self.current_speed == 0:
                    # lift is not moving, waiting for a new aim
                    self.event_for_engine.wait()
                # else: new intermediate aim was added

                self.event_for_engine.clear()
                with self.lock:
                    new_aim = self.new_aim

                # brute stop
                if new_aim == 'Q':
                    self.current_storey = 'Q'
                    break

                print('engine: change aim ' + str(self.current_aim) + ' -> ' + str(new_aim))
                self.current_aim = new_aim
                self.current_aim_storey = self.current_aim[0]
                self.update_speed()

            time.sleep(1)

            with self.lock:
                self.current_storey += self.current_speed
                current_storey = self.current_storey

            message = 'current_storey: ' + str(current_storey) + ' (aim: ' + str(self.current_aim_storey) + ')'
            self.information_board_queue.put(message)
            if current_storey == self.current_aim_storey:
                self.current_speed = 0
                self.strategy_module.remove_aim(self.current_aim)
                self.light_controller.turn_light_on()
                while True:
                    self.door_controller.release_passengers(self.weight_sensor)
                    if self.weight_sensor.is_limit_exceeded():
                        continue
                    if self.weight_sensor.is_empty():
                        self.light_controller.turn_light_off()
                    break
                print('engine: change aim ' + str(self.current_aim) + ' -> ' + 'None')
                self.current_aim = None

    def run(self):
        thread_new_aim_checker = threading.Thread(target=self.run_check_new_aim)
        thread_engine = threading.Thread(target=self.run_engine)

        thread_new_aim_checker.start()
        thread_engine.start()
        self.strategy_module.run()

        print('strategy module stopped')
        thread_new_aim_checker.join()
        print('aim checker stopped')
        thread_engine.join()
        print('engine stopped')
