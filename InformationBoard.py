
class InformationBoard(object):

    def __init__(self, motion_controller_queue):
        self.motion_controller_queue = motion_controller_queue

    def run(self):
        while True:
            lift_storey = self.motion_controller_queue.get()
            print('information_board: ', lift_storey)
