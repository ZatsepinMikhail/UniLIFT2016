import time

class DoorController(object):

    def __init__(self):
        self.is_open = False
        self.TIME_NEEDED_FOR_OPENING = 0.5
        self.DOORS_OPEN_INTERVAL = 3

    def open_doors(self):
        self.is_open = True

    def close_doors(self):
        self.is_open = False

    def get_open_state(self):
        return self.is_open

    def release_passengers(self, weight_sensor):
        assert not self.is_open, 'Doors are open, function shouldn\'t have been called'
        time.sleep(self.DOORS_OPEN_INTERVAL)
        self.open_doors()
        print('door_controller: doors are open')
        time.sleep(self.DOORS_OPEN_INTERVAL // 2)
        weight_sensor.simulate_setting_weight()
        time.sleep(self.DOORS_OPEN_INTERVAL // 2)
        self.close_doors()
        time.sleep(self.DOORS_OPEN_INTERVAL)
        print('door_controller: doors are closed')
