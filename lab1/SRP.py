import enum
import time

from net import Package, Codes
from logger import Logger


class Status(enum.Enum):
    ACTIVE = enum.auto()
    OUTDATED = enum.auto()
    DERIVED = enum.auto()


class Help:
    def __init__(self, status=Status.OUTDATED):
        self.status = status
        self.timestamp = time.time()


class Sender(Logger):
    def __init__(self, msg_count, window_size=2, timeout=0.1):
        super().__init__('SRP Sender')
        self._window_size = window_size
        self._timeout = timeout
        self._msg_count = msg_count

    def run(self, input, output, data=(), need_print=True):
        if not data:
            data = None,
        data_len = len(data)
        term_index = data_len - 1
        approved = 0
        window_size = min(self._window_size, data_len)
        nodes = {i: Help() for i in range(window_size)}

        while approved < data_len:
            if input:
                msg = self.channel_pop(input, need_print)
                approved += 1
                nodes[msg.index].status = Status.DERIVED

            for node in nodes.values():
                if time.time() - node.timestamp > self._timeout and node.status != Status.DERIVED:
                    node.status = Status.OUTDATED

            keys = list(nodes.keys())
            for index in keys:
                assert len(nodes) == window_size
                max_key = max(nodes.keys())
                code = Codes.TERM if index == term_index else Codes.NONE
                if nodes[index].status == Status.OUTDATED:
                    nodes[index].timestamp = time.time()
                    nodes[index].status = Status.ACTIVE
                    package = Package(index=index, code=code, data=data[index])
                    self.channel_append(output, package, need_print)
                    self._msg_count.value += 1
                elif nodes[index].status == Status.DERIVED:
                    if max_key < term_index:
                        del nodes[index]
                        nodes[max_key + 1] = Help()
        bar = 1
        bar *= 2


class Receiver(Logger):
    def __init__(self, result):
        super().__init__('SRP Receiver')
        self.data = result

    def run(self, input, output, need_print=True):
        data = {}
        term_flag = False
        while True:
            if input:
                msg = self.channel_pop(input, need_print)
                if msg.code == Codes.TERM:
                    term_flag = True
                data[msg.index] = msg.data
                package = Package(index=msg.index, code=Codes.APPROVE)
                self.channel_append(output, package, need_print)
                if term_flag and sorted(list(data.keys())) == list(range(len(data))):
                    for x in filter(lambda item: item is not None, sorted(data.values())):
                        self.data.put(x)
                    break