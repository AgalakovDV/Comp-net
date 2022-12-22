from collections import namedtuple
from random import random
from enum import IntEnum


class Codes(IntEnum):
    NONE = 0
    APPROVE = 1
    TERM = 2
    ERROR = 3


Package = namedtuple('Package', field_names=['index', 'code', 'data'], defaults=[0, 0, None])


class Channel:
    def __init__(self, q,  loss_chance=0.0):
        self._loss_chance = min(1.0, max(0.0, loss_chance))
        self._queue = q

    @property
    def loss_chance(self):
        return self._loss_chance

    @loss_chance.setter
    def loss_chance(self, loss_chance):
        self._loss_chance = min(1.0, max(0.0, loss_chance))

    def __len__(self):
        return self._queue.qsize()

    def __bool__(self):
        l = self._queue.empty()
        if not l:
            b = self._queue
            # print(l)
        return not l

    def append(self, package):
        if random() >= self.loss_chance:
            self._queue.put(package)
            return True
        return False

    def pop(self):
        l = self._queue.qsize()
        if l == 0:
            return None
        return self._queue.get()

    def clear(self):
        while not self._queue.empty():
            self._queue.get()
