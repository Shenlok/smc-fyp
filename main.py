from multiprocessing import Process
import subprocess
import time

def launch_psa(num):
    subprocess.call(["python", "psa-viff.py", "local-{0}.ini".format(num)])

def launch_rass(num):
    subprocess.call(["python", "rass-viff.py", "local-{0}.ini".format(num)])

if __name__ == '__main__':
    players = []
    print "Launching PSAs"
    for x in range(0, 4):
        p = Process(target=launch_psa, args=('{0}'.format(x+1),))
        p.start()
        players.append(p)

    for p in players:
        p.join()

    time.sleep(2)

    players = []
    print "Launching RASSs"
    for x in range(0, 4):
        p = Process(target=launch_rass, args=('{0}'.format(x+1),))
        p.start()
        players.append(p)

    for p in players:
        p.join()
