import pickle
pickle.HIGHEST_PROTOCOL = 2

from multiprocessing import cpu_count, Process
from redis import Redis
from rq import Worker
from util import solve

def process():
    c = Redis(host='192.168.1.237')
    w = Worker(['default'], connection=c)
    w.work()

if __name__ == '__main__':
    n = cpu_count()
    ps = []
    for i in range(n):
        p = Process(target=process, args=())
        p.start()
        ps.append(p)
    for p in ps:
        p.join()
