class ButtonHandler:

    def __init__(self, button_queue):
        self.button_queue = button_queue

    def handle_button_pressure(self, button):
        print 'process button ', button

    def simulate_work(self):
        while True:
            buttonPressed = self.button_queue.get()
            self.handle_button_pressure(buttonPressed)
