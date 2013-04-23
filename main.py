from multiprocessing import Process
import subprocess
import time
from psa import PSA
import cProfile
import sys
import os
import math
import pollard

from timeit import default_timer
import random
import matplotlib.pyplot as plt
import numpy as np

def launch_psa(num):
    subprocess.call(["python", "psa-viff.py", "local-{0}.ini".format(num)])

def launch_rass(num):
    subprocess.call(["python", "rass-viff.py", "local-{0}.ini".format(num)])

def avg(s):
    return sum(s) / len(s)

def variance(s):
    return map(lambda x: (x - average(s)**2, s))

def std_dev(s):
    return math.sqrt(average(variance(s)))

if __name__ == '__main__':
    '''
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
    '''
    print "Beginning black-box benchmarks"
    if not os.path.exists("./logs"):
        os.mkdir("logs")

    if not os.path.exists("./graphs"):
        os.mkdir("graphs")

    #sys.stdout = open("logs/log-{0}-psa.txt".format(id), "w")



    protocol = PSA()

    id = 1

    n = 4

    #p = 8210367885679168766758950738484631605814497398518690371786648569002948704711364117378465988124313755366044696642284768924819556022676696987591359662994541674288334772534600049590413961300804080139388895971566128327100549100994100446988248682535394236326347178554088960814072469643139825048533231637837365239
    #p = 83
    p = 0
    t = 0.33

    b = 8 # Bit length of our message space

    delta = (2**b) - 1
    #delta = 5
    k = 256

    rand = random.SystemRandom()

    encTimes = {}
    decTimes = {}

    while b <= 64:
        n = 4
        encTimes[b] = {}
        decTimes[b] = {}
        while n <= 100:
            print "Benchmarks for b = {0} n = {1}".format(b, n)
            start = default_timer()
            params, sks = protocol.setup(n, t, delta, k, p)
            end = default_timer()
            print "Setup took {0}".format(end - start)

            # Testing everything is working as it should
            '''elems = []
            for x in xrange(6):
                elems.append(rand.randint(0, p-1))'''
            '''elems = sks
            v = sum(elems) % params.Zq.modulus
            assert v == 0

            w = reduce(lambda x, y: x*y, map(lambda x: params.g**x, elems))
            Zp = params.Zp
            assert type(w) == type(Zp(0))
            assert type(params.g) == type(Zp(0))
            assert type(w) == type(params.g)
            #log = pollard.discrete_log_lambda(w, params.g, (0, params.Zq.modulus-1))
            log = pollard.discrete_log_rho(w, params.g, params.Zp.modulus)
            print "Given elems = {0}, v = {1}, w = {2}, g = {3} and log = {4}".format(elems, v, w, params.g, log)
            assert log == v'''


            

            cs = []
            encTimes[b][n] = []
            inputs = []
            for sk in sks[1:]:
                start = default_timer()
                input = rand.randint(0, delta)
                
                c, xbar = protocol.NoisyEnc(params, sk, 1, input)
                inputs.append(xbar)     
                end = default_timer()
                cs.append(c)
                encTimes[b][n].append(end - start)       
            
            decTimes[b][n] = []
            start = default_timer()
            theSum = reduce(lambda x, y: (x + y) % params.Zp.modulus, inputs)
            print "Sum: {0}".format(theSum)
            prod = protocol.AggrDec(params, sks[0], 1, cs)
            if prod == None:
                print "AggrDec failed to find log for values: xbars = {0}\n sk0 = {1}\n".format(inputs, sks[0])
            else:
                print "AggrDec calculated: {0}".format(prod)
            end = default_timer()
            decTimes[b][n].append(end - start) 
            n *= 2
        b *= 2
        delta = (2**b) - 1
        #delta = 5

    for b in encTimes.keys():
        fig = plt.figure()
        ax = fig.subplot(111)
        avgTimes = {}
        
        for (n, nTimes) in zip(encTimes[b].keys(), encTimes[b].values()):
            avgTimes[n] = (average(nTimes), std_dev(nTimes))

        for n in avgTimes.keys():
            pass

        plt.plot(avgTimes.keys(), avgTimes.values())
        plt.savefig("graphs/psa-noisyenc-b{0}.png".format(b))
        plt.close()
    
