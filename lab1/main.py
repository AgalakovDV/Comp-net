import numpy as np
import seaborn as sns
import matplotlib as mpl

from multiprocessing import Process as Thread
from multiprocessing import Queue, Value
from time import perf_counter
from matplotlib import pyplot as plt
from tqdm.notebook import tqdm

from net import Network
from GBN import Sender as SenderGBN, Receiver as ReceiverGBN
from SRP import Sender as SenderSRP, Receiver as ReceiverSRP

sns.set(color_codes=True)
mpl.rcParams['figure.dpi'] = 120
my_len = 50


def my_plot(x, y, xlabel=None, ylabel=None, title=None, **kwargs):
    plt.plot(x, y, **kwargs)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    if title:
        plt.title(title)


def work(winsize, timeout, prob_lost):
    main_q = Queue()
    back_q = Queue()
    result = Queue()
    msgs = Value('i', 0)

    sender = Sender(msgs, winsize=winsize, timeout=timeout)
    receiver = Receiver(result)

    main_ch = Network(main_q, prob_lost=prob_lost)
    back_ch = Network(back_q, prob_lost=0)
    sender_thread = Thread(target=sender.run, args=(back_ch, main_ch, data, False))
    receiver_thread = Thread(target=receiver.run, args=(main_ch, back_ch, False))

    time_start = perf_counter()
    sender_thread.start()
    receiver_thread.start()
    sender_thread.join()
    receiver_thread.join()
    time_elapsed = perf_counter() - time_start

    r = []
    while not receiver.data.empty():
        r.append(receiver.data.get())

    return msgs.value, time_elapsed
	

if __name__ == '__main__':
    data = list(range(my_len))
    N = 2

    for prob_lost in tqdm([0, 0.5]):
        timeout = 0.1
        window_sizes = list(range(1, 11))
        msgs_sent = {}
        time_spent = {}
    
        for Sender, Receiver in (SenderSRP, ReceiverSRP), (SenderGBN, ReceiverGBN):
            protocol = 'GBN' if Sender == SenderGBN else 'SRP'
            msgs_sent[protocol] = []
            time_spent[protocol] = []
        
            for winsize in tqdm(window_sizes):
                msgs = []
                time_elapsed = []
                for _ in range(N):
                    msgs_ex, time_elapsed_ex = work(winsize, timeout, prob_lost)
                    msgs.append(msgs_ex)
                    time_elapsed.append(time_elapsed_ex)
                
                msgs_sent[protocol].append(np.mean(msgs))
                time_spent[protocol].append(np.mean(time_elapsed))
            
        title = f'loss chance = {prob_lost}, timeout = {timeout}'
    
        my_plot(window_sizes, msgs_sent['GBN'], 'window size', 'messages', title, label='GBN')
        my_plot(window_sizes, msgs_sent['SRP'], label='SRP')
        plt.legend()
        plt.show()

        my_plot(window_sizes, time_spent['GBN'], 'window size', 'time spent', title, label='GBN')
        my_plot(window_sizes, time_spent['SRP'], label='SRP')
        plt.legend()
        plt.show()
        print(title)

        winsize = 5
        msgs_sent = {}
        time_spent = {}
        timeouts = np.linspace(0.1, 1, num=11)
    
        for Sender, Receiver in (SenderGBN, ReceiverGBN), (SenderSRP, ReceiverSRP):
            protocol = 'GBN' if Sender == SenderGBN else 'SRP'
            msgs_sent[protocol] = []
            time_spent[protocol] = []
        
            for timeout in tqdm(timeouts):
                msgs = []
                time_elapsed = []
                for _ in range(N):
                    msgs_ex, time_elapsed_ex = work(winsize, timeout, prob_lost)
                    msgs.append(msgs_ex)
                    time_elapsed.append(time_elapsed_ex)
                
                msgs_sent[protocol].append(np.mean(msgs))
                time_spent[protocol].append(np.mean(time_elapsed))
                
        title = 'loss chance = {}, window size = {}'.format(prob_lost, winsize)

        my_plot(timeouts, msgs_sent['GBN'], 'timeout', 'messages', title, label='GBN')
        my_plot(timeouts, msgs_sent['SRP'], label='SRP')
        plt.legend()
        plt.show()

        my_plot(timeouts, time_spent['GBN'], 'timeout', 'time spent', title, label='GBN')
        my_plot(timeouts, time_spent['SRP'], label='SRP')
        plt.legend()
        plt.show()
        print(title)