from multiprocessing import Process as Thread, Lock, Queue, Value
import time
from channel import Channel
from SRP import Sender, Receiver


class Host:
    def __init__(self):
        self._sender = Sender(window_size=5, timeout=1)
        result = Queue()
        self._receiver = Receiver(result)
        main_q = Queue()
        back_q = Queue()
        self._channel_main = Channel(main_q)
        self._channel_back = Channel(back_q)
        self._sender_thread = None
        self._receiver_thread = None
        self._msg_flag = Value('i', 0)
        self.mutex = Lock()

    def push(self, data=None):
        self.mutex.acquire()
        self._receiver.clear_data()
        self._channel_main.clear()
        self._channel_back.clear()
        self._sender_thread = Thread(target=self._sender.run,
                                     args=(self._channel_back, self._channel_main, (data,), False))
        self._receiver_thread = Thread(target=self._receiver.run,
                                       args=(self._channel_main, self._channel_back, False))
        self._sender_thread.start()
        self._receiver_thread.start()
        self._sender_thread.join()
        self._receiver_thread.join()
        self._msg_flag.value = 1
        self.mutex.release()

    def get(self):
        while True:
            self.mutex.acquire()
            if self._msg_flag.value:
                self._msg_flag.value = 0
                data = self._receiver.get()
                self._receiver.clear_data()
                self.mutex.release()
                break
            self.mutex.release()
            time.sleep(0.1)
        return data


