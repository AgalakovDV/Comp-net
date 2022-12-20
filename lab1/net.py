from collections import namedtuple
from random import random
from enum import IntEnum


class Codes(IntEnum):
    NONE = 0
    APPROVE = 1
    TERM = 2
    ERROR = 3


Package = namedtuple('Package', field_names=['index', 'code', 'data'], defaults=[0, 0, None])


class Network:
    def __init__(self, q,  prob_lost=0.0):
        self._prob_lost = min(1.0, max(0.0, prob_lost))
        self._queue = q

    def __bool__(self):
        l = self._queue.empty()
        if not l:
            b = self._queue
        return not l
        
    def __len__(self):
        return self._queue.qsize()

    def pop(self):
        l = self._queue.qsize()
        if l == 0:
            return None
        return self._queue.get()

    def append(self, package):
        if random() >= self.prob_lost:
            self._queue.put(package)
            return True
        return False

    @property
    def prob_lost(self):
        return self._prob_lost

    @prob_lost.setter
    def prob_lost(self, prob_lost):
        self._prob_lost = min(1.0, max(0.0, prob_lost))
    