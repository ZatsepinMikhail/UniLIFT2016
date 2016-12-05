import time


class LightController(object):

    def __init__(self):
        self.is_light_on = False

    def turn_light_on(self):
        self.is_light_on = True
        # print 'light_controller: light turns on'

    def turn_light_off(self):
        self.is_light_on = False
        # print 'light_controller: light turns off'
