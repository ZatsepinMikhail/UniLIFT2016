import time


class DoorController(object):

    def __init__(self):
        self.is_open = False
        self.DOORS_OPEN_INTERVAL = 3

    def open_doors(self):
        print 'door_controller: doors are opening'
        time.sleep(0.5)
        self.is_open = True

    def close_doors(self):
        print 'door_controller: doors are closing'
        time.sleep(0.5)
        self.is_open = False

    def is_open(self):
        return self.is_open

    def release_passengers(self, weight_sensor):
        assert not self.is_open, 'Doors are open, function shouldn\'t have been called'
        self.open_doors()
        time.sleep(self.DOORS_OPEN_INTERVAL)
        weight_sensor.simulate_setting_weight()
        self.close_doors()
