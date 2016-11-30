import multiprocessing
import buttons
import button_handler
import strategy_module
import time

if __name__ == '__main__':

    #queue buttons - button_handler
    queue_buttons_bh = multiprocessing.Queue()

    #queue button_handler - strategy_module
    queue_bh_sm = multiprocessing.Queue()
    storey_num = 10

    button_handler = button_handler.ButtonHandler(queue_buttons_bh, queue_bh_sm)

    process_buttons = multiprocessing.Process(target=buttons.simulate_buttons_pressure, args=(storey_num, queue_buttons_bh))
    process_button_handler = multiprocessing.Process(target=button_handler.run)
    process_strategy_module = multiprocessing.Process(target=strategy_module.init_run, args=(queue_bh_sm, ))

    process_buttons.start()
    process_button_handler.start()
    process_strategy_module.start()

    time.sleep(100)

    process_buttons.join()
    process_button_handler.join()
    process_strategy_module.join()

    queue_buttons_bh.close()
    queue_bh_sm.close()
