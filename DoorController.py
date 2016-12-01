import time

class DoorController(object):

    def __init__(self):
        self.is_open = False
        self.DOORS_OPEN_INTERVAL = 3

    def open_doors(self):
        self.is_open = True

    def close_doors(self):
        self.is_open = False

    def is_open(self):
        return self.is_open

    def release_passengers(self, weight_sensor):
        assert not self.is_open, 'Doors are open, function shouldn\'t have been called'
        self.open_doors()
        print 'door_controller: doors are open'
        time.sleep(self.DOORS_OPEN_INTERVAL)
        weight_sensor.simulate_setting_weight()
        self.close_doors()
        print 'door_controller: doors are closed'
