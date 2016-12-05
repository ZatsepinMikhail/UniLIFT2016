
class InformationBoard(object):

    def __init__(self, motion_controller_queue):
        self.motion_controller_queue = motion_controller_queue

    def run(self):
        while True:
            message = self.motion_controller_queue.get()

            # poison pill
            if message == 'Q':
                break

            print('information_board: ', message)
