from fabric.connection import Connection
import threading
import pickle
pickle.HIGHEST_PROTOCOL = 2

hosts = [
    'Rpi1',
    'Rpi2',
    'Rpi3',
    'Rpi4',
]

class Pool():
    def __init__(self):
        self.p = []

    def add(self, a):
        self.p+=[a]

    def run(self, a):
        threads = []
        for i in self.p:
            t = threading.Thread(target=i.run, args=(a,))
            t.start()
            threads += [t]

        for i in threads:
            i.join()

    def sudo(self, a):
        threads = []
        for i in self.p:
            t = threading.Thread(target=i.sudo, args=(a,))
            t.start()
            threads += [t]

        for i in threads:
            i.join()

    def put(self, a, b):
        threads = []
        for i in self.p:
            t = threading.Thread(target=i.put, args=(a, b))
            t.start()
            threads += [t]

        for i in threads:
            i.join()

pool = Pool()

for i in hosts:
    conn = Connection("{username}@{ip}:{port}".format(username="pi",ip=i,port=22),connect_kwargs={"password": "1597"})
    pool.add(conn)

def update():
    print(pool.run('whoami'))
    pool.sudo('apt-get update')
    pool.sudo('apt-get dist-upgrade -y')

def test():
    print(pool.run("echo 'hi'>bernardi.log"))

def reboot():
    # reboot hosts
    pool.sudo('shutdown -r now')

def shutdown():
    # shutdown hosts
    pool.run('echo "1597" | sudo -S shutdown -h now')

def setup():
    # setup hosts (install dependencies)
    pool.sudo('apt-get install -y python3-pip')
    pool.sudo('pip3 install rq redis rsa')

def pygraham_install():
    pool.sudo('pip3 install pygraham')

def install_dill():
    pool.sudo('pip3 install dill')

def upload():
    # upload code to hosts
    pool.put('util.py', 'util.py')
    pool.put('worker.py', 'worker.py')

def start():
    # start worker.py scripts
    pool.run('python3 worker.py')
