from multiprocessing import Process as Thread, Barrier
from general import General


if __name__ == '__main__':
    n_generals = 5
    barrier = Barrier(n_generals)
    generals = [General(i, barrier) for i in range(n_generals - 1)]
    generals.append(General(n_generals - 1, barrier, True))
    for g1 in generals:
        for g2 in generals:
            if g1 != g2:
                g1.connect(g2)
    threads = [Thread(target=g.run) for g in generals]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
