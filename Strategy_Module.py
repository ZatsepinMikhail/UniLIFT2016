import Queue

class StrategyModule:

    def __init__(self, button_handler_queue, strategy_module_event):
        self.priority_queue = Queue.PriorityQueue()
        self.button_handler_queue = button_handler_queue
        self.strategy_module_event = strategy_module_event

    #aim = [storey, inner-outer]
    def add_new_aim(self, new_aim):
        print 'insert new aim ', new_aim
        previous_first_aim = [-1, False]
        if not self.priority_queue.empty():
            previous_first_aim = self.priority_queue.queue[0]

        self.priority_queue.put(new_aim)

        #get min value from priority queue
        updated_first_aim = self.priority_queue.queue[0]
        if previous_first_aim != updated_first_aim:
            print 'notify motion controller', previous_first_aim, ' -> ', updated_first_aim
            self.strategy_module_event.set()
        else:
            #print previous_first_aim, updated_first_aim
            pass

    def get_new_aim(self):
        self.strategy_module_event.clear()
        return self.priority_queue.queue[0]

    def remove_aim(self, aim):
        pass

    def run(self):
        while True:
            new_aim = self.button_handler_queue.get()
            self.add_new_aim(new_aim)

