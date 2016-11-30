import random
from time import sleep

class Button:

    def __init__(self, storey, inner_button):
        self.pressed = False
        self.storey = storey
        self.inner_button = inner_button
        #self.button_handler = button_handler

    def is_pressed(self):
        return self.pressed

    def press(self):
        self.pressed = True

    def get_storey(self):
        return self.storey

def simulate_buttons_pressure(storey_num, queue):

    buttons = []
    for i in xrange(1, storey_num + 1):
        buttons.append(Button(i, False))

    num_button_pressed = 0
    while True:
        sleep(random.random())
        random_button_number = random.randint(0, len(buttons) - 1)
        button = buttons[random_button_number]
        if not button.is_pressed():
            button.press()
            num_button_pressed += 1
            queue.put(button.get_storey())
            #print 'Buttons: ', button.get_storey()

        if num_button_pressed == len(buttons):
            #print 'Buttons: all buttons have been pressed. Exit'
            break
