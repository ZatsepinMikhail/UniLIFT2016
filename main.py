import multiprocessing
import buttons

if __name__ == '__main__':
    queue = multiprocessing.Queue()
    storey_num = 10

    p = multiprocessing.Process(target=buttons.simulate_buttons_pressure, args=(storey_num, queue))
    p.start()

    num_received_messages = 0
    while storey_num != num_received_messages:

        storey = queue.get()
        print 'Main: button ', storey, ' pressed'

        num_received_messages += 1
