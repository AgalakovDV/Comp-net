from collections import Counter
from multiprocessing import Process as Thread, Lock
from host import Host
from tabulate import tabulate


class NetworkNode:
    def __init__(self, index, barrier):
        self.index = index
        self.barrier = barrier
        self._in_connections = {}
        self._out_connections = {}

    def connect(self, other):
        self._in_connections[other.index] = Host()
        other.add_out_conn(self.index, self._in_connections[other.index])
        self._out_connections[other.index] = Host()
        other.add_in_conn(self.index, self._out_connections[other.index])

    def add_in_conn(self, index, channel):
        self._in_connections[index] = channel

    def add_out_conn(self, index, channel):
        self._out_connections[index] = channel

    def sendall(self, values):
        pairs = zip(self._out_connections.values(), values)
        sender_threads = [Thread(target=c.push, args=(v,)) for c, v in pairs]
        for thread in sender_threads:
            thread.start()
        for thread in sender_threads:
            thread.join()
        return {i: c.get() for i, c in self._in_connections.items()}


class General(NetworkNode):
    def __init__(self, index, barrier, byzantine=False):
        super(General, self).__init__(index, barrier)
        self.byzantine = byzantine
        self.result = []
        self.mutex = Lock()

    def run(self):
        values = ['f' + str(i) if self.byzantine else 't' + str(self.index) for i in self._out_connections.keys()]
        t1_results = self.sendall(values)

        self.barrier.wait()
        self.barrier.reset()

        self.mutex.acquire()
        print(f"General {self.index} got: \n"
              f"{tabulate([[x, t1_results[x]] for x in t1_results], headers=['Генерал', 'Информация'], tablefmt='outline')}\n")
        self.mutex.release()

        if self.byzantine:
            pattern = 'f{}{}'
            values = []
            for i in self._out_connections.keys():
                column = t1_results.copy()
                for j in column.keys():
                    column[j] = pattern.format(i, j)
                values.append(column)
        else:
            values = [t1_results for i in self._out_connections.keys()]

        t2_results = self.sendall(values)

        self.mutex.acquire()
        print(f"General {self.index} have formed: \n"
              f"{tabulate([[x, t2_results[x]] for x in t2_results], headers=['Генерал', 'Информация'], tablefmt='outline')}\n")
        self.mutex.release()

        self.barrier.wait()

        info_matrix = list(t2_results.values())
        info_matrix.append(t1_results)
        indices = set()
        for column in info_matrix:
            for index in column.keys():
                indices.add(index)
        result = {}
        for index in indices:
            counter = Counter()
            for column in info_matrix:
                if index in column.keys():
                    counter[column[index]] += 1
            common = counter.most_common(2)
            if len(common) > 1 and common[0][1] == common[1][1]:
                result[index] = 'None'
            else:
                result[index] = common[0][0]
        keys = sorted(list(result.keys()))
        result_sorted = {k: result[k] for k in keys}

        self.mutex.acquire()
        print(f"--Гнерал {self.index}-- result: \n"
              f"{tabulate([[x, result_sorted[x]] for x in result_sorted], headers=['Генерал', 'Информация'], tablefmt='outline')}\n")
        self.mutex.release()
