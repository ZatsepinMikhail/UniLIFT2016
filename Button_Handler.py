class ButtonHandler:

    def __init__(self, button_queue, strategy_module_queue):
        self.button_queue = button_queue
        self.strategy_module_queue = strategy_module_queue

    def handle_button_pressure(self, button):
        print 'button_handler: process button ', button
        self.strategy_module_queue.put(button)

    def run(self):
        while True:
            buttonPressed = self.button_queue.get()
            self.handle_button_pressure(buttonPressed)
