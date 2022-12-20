import time

from net import Package, Codes
from logger import Logger


class Sender(Logger):
    def __init__(self, msg_count, window_size=2, timeout=0.1):
        super().__init__('GBN Sender')
        self._window_size = window_size
        self._timeout = timeout
        self.sends = 0
        self._msg_count = msg_count

    def run(self, input, output, data=(), need_print=True):
        if not data:
            data = None,
        current_index = 0
        approved_index = -1
        term_index = len(data) - 1
        begin_waiting = time.time()
        while approved_index < term_index:
            if time.time() - begin_waiting > self._timeout:
                begin_waiting = time.time()
                current_index = approved_index + 1
                continue
            if input:
                msg = self.channel_pop(input, need_print)
                begin_waiting = time.time()
                if msg.index == approved_index + 1 and msg.code == Codes.APPROVE:
                    approved_index += 1
                else:
                    current_index = approved_index + 1
                continue
            if current_index <= min(approved_index + self._window_size, term_index):
                code = Codes.TERM if current_index == term_index else Codes.NONE
                package = Package(index=current_index, code=code, data=data[current_index])
                self.channel_append(output, package, need_print)
                self._msg_count.value += 1
                current_index += 1
                continue
        bar = 1
        bar *= 2


class Receiver(Logger):
    def __init__(self, result):
        super().__init__('GBN Receiver')
        self.data = result

    def run(self, input, output, need_print=True):
        expected = 0
        while True:
            if input:
                msg = self.channel_pop(input, need_print)
                if msg.index == expected:
                    package = Package(index=msg.index, code=Codes.APPROVE)
                    self.channel_append(output, package, need_print)
                    expected += 1
                    if msg.data is not None:
                        self.data.put(msg.data)
                    if msg.code == Codes.TERM:
                        return
                else:
                    data = 'expected {}, got {}'.format(expected, msg.index)
                    package = Package(index=-1, code=Codes.ERROR, data=data)
                    self.channel_append(output, package, need_print)
                continue
            # time.sleep(0.05)