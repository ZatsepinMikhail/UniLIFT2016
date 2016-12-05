import threading
import bisect
import time
from OrderedSet import OrderedSet
import heapq

from DoorController import *
from LightController import *
from WeightSensor import *


class MotionController(object):

    class StrategyModule(object):

        def __init__(self, button_handler_queue, motion_controller):

            # set of incoming aims
            self.aim_set = OrderedSet()
            self.aims_intermediate = []  # heap
            self.aim_main = None
            # self.is_main_returned = False

            self.button_handler_queue = button_handler_queue
            self.motion_controller = motion_controller

        def get_nearest_aim(self):
            assert len(self.aim_set) != 0 or self.aim_main is not None, 'Function cannot be called if there are no ' \
                                                                        'new aims'
            if self.aim_main is not None:
                # lock due to current_storey and aims_intermediate
                self.motion_controller.lock.acquire()
                if not self.aims_intermediate:
                    res = self.aim_main
                else:
                    while not self.is_intermediate_aim(self.aims_intermediate[0]):
                        heapq.heappop(self.aims_intermediate)
                    res = self.aims_intermediate[0]
                self.motion_controller.lock.release()
            else:
                # define new main aim
                self.aim_main = next(x for x in self.aim_set)
                # update intermediate aims
                for aim in self.aim_set:
                    if self.is_intermediate_aim(aim[0]):
                        pass
                res = self.aim_main

            print 'strategy: chose', res
            return res

        def is_intermediate_aim(self, storey_check, storey_from = None, storey_to = None):
            if storey_to is None:
                storey_to = self.aim_main[0]
            if storey_from is None:
                self.motion_controller.lock.acquire()
                storey_from = self.motion_controller.current_storey
                self.motion_controller.lock.release()
            return max(storey_from, storey_to) - 1 >= storey_check >= min(storey_from, storey_to) + 1

        # aim = [storey, inner-outer]
        def add_new_aim(self, new_aim):
            if self.aim_main is not None:
                # check if such an aim exists in set
                if new_aim not in self.aim_set:
                    # add new_aim to the set
                    self.aim_set.add(new_aim)

                    # update heap of intermediate aims
                    if self.is_intermediate_aim(new_aim[0]):
                        heapq.heappush(self.aims_intermediate, new_aim[0])
            elif not self.aim_set:
                self.aim_set.add(new_aim)
                self.motion_controller.event_new_aim.set()
            else:
                self.aim_set.add(new_aim)
            print 'add_new_aim: set at the end:', self.aim_set

        def get_new_aim(self):
            self.motion_controller.event_new_aim.clear()
            return self.get_nearest_aim()

        def remove_aim(self, aim):
            self.aim_set.remove(aim)
            if self.aim_main == aim:
                self.aim_main = None
            if self.aims_intermediate and self.aims_intermediate[0] == aim[0]:
                heapq.heappop(self.aims_intermediate)
            if self.aim_set:
                self.motion_controller.event_new_aim.set()
                print 'exiting remove_aim'

        def run(self):
            while True:
                new_aim = self.button_handler_queue.get()
                self.add_new_aim(new_aim)
                print 'strategy_module: got new aim ' + str(new_aim) + '. Set:', self.aim_set

    def __init__(self, button_handler_queue, weight_limit):
        self.event_new_aim = threading.Event()
        self.event_for_engine = threading.Event()
        self.strategy_module = MotionController.StrategyModule(button_handler_queue, self)
        self.current_storey = 1

        # -1, 0, 1
        self.current_speed = 0
        self.current_aim = None
        self.current_aim_storey = None
        self.new_aim = None
        self.lock = threading.Lock()

        self.door_controller = DoorController()
        self.light_controller = LightController()
        self.weight_sensor = WeightSensor(weight_limit)

    def get_current_storey(self):
        return self.current_storey

    def run_check_new_aim(self):
        while True:
            self.event_new_aim.wait()
            self.new_aim = self.strategy_module.get_new_aim()
            print 'motion_controller: got new aim ', self.new_aim
            self.event_for_engine.set()

    def run_engine(self):
        while True:
            if self.current_speed == 0:
                self.event_for_engine.wait()
                # lift is not moving, new aim caught

                # bad decision
                self.event_for_engine.clear()
                self.current_aim = self.new_aim
                self.current_aim_storey = self.current_aim[0]

                if self.current_aim_storey > self.current_storey:
                    self.current_speed = 1
                elif self.current_aim_storey < self.current_storey:
                    self.current_speed = -1

            elif self.event_for_engine.is_set():
                # new intermediate aim was added
                print 'engine: change aim ' + str(self.current_aim) + ' -> ' + str(self.new_aim)
                self.current_aim = self.new_aim
                self.current_aim_storey = self.current_aim[0]
                if self.current_aim_storey > self.current_storey:
                    self.current_speed = 1
                elif self.current_aim_storey < self.current_storey:
                    self.current_speed = -1

            time.sleep(1)

            self.lock.acquire()
            self.current_storey += self.current_speed
            print 'engine: current_storey', self.current_storey, '(aim: ' + str(self.current_aim_storey) + ')'
            if self.current_storey == self.current_aim_storey:
                self.current_speed = 0
                # self.light_controller.turn_light_on()
                # while True:
                #     self.door_controller.release_passengers(self.weight_sensor)
                #     if self.weight_sensor.is_limit_exceeded():
                #         continue
                #     if self.weight_sensor.is_empty():
                #         self.light_controller.turn_light_off()
                #     break
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
