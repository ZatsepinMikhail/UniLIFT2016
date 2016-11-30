import multiprocessing
import buttons
import button_handler
import time

if __name__ == '__main__':
    queue = multiprocessing.Queue()
    storey_num = 10

    button_handler = button_handler.ButtonHandler(queue)

    process_buttons = multiprocessing.Process(target=buttons.simulate_buttons_pressure, args=(storey_num, queue))
    process_button_handler = multiprocessing.Process(target=button_handler.simulate_work)

    process_buttons.start()
    process_button_handler.start()

    time.sleep(1)

    process_buttons.join()
    process_button_handler.join()
    queue.join()


