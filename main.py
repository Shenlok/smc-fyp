from multiprocessing import Process
import subprocess

def launch_psa(num):
    subprocess.call(["python", "psa-viff.py", "local-{0}.ini".format(num)])

if __name__ == '__main__':
    players = []
    for x in range(0, 4):
        p = Process(target=launch_psa, args=('{0}'.format(x+1),))
        p.start()
        players.append(p)

    for p in players:
        p.join()
