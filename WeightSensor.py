import random


class WeightSensor(object):

    def __init__(self, weight_limit):
        self.weight = 0
        self.weight_limit = weight_limit

    def get_weight(self):
        print 'weight sensor: current weight', self.weight
        return self.weight

    def is_limit_exceeded(self):
        return self.get_weight() > self.weight_limit

    def is_empty(self):
        return self.get_weight() == 0

    # simulate passengers
    def simulate_setting_weight(self):
        self.weight = random.randint(0, 5) * 50
        print 'weight sensor: set weight', self.weight
