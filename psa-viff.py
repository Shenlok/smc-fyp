from optparse import OptionParser
import viff.reactor
viff.reactor.install()
from twisted.internet import reactor
from psa import PSA
import cProfile
import sys
import os
from viff.runtime import create_runtime, Runtime
from viff.config import load_config
from timeit import default_timer
import random

parser = OptionParser()
Runtime.add_options(parser)
(options, args) = parser.parse_args()

if len(args) == 0:
    parser.error("you must specify a config file")
else:
    id, players = load_config(args[0])

if not os.path.exists("./logs"):
    os.mkdir("logs")
sys.stdout = open("logs/log-{0}-psa.txt".format(id), "w")

protocol = PSA()

n = len(players)

p = 8210367885679168766758950738484631605814497398518690371786648569002948704711364117378465988124313755366044696642284768924819556022676696987591359662994541674288334772534600049590413961300804080139388895971566128327100549100994100446988248682535394236326347178554088960814072469643139825048533231637837365239

t = 0.33

b = 16 # Bit length of our message space

delta = (2**b) - 1

k = 1024

rand = random.SystemRandom()

def doPsa(runtime):
    print "I am player {0}".format(runtime.id)
    start = default_timer()
    params, sks = protocol.setup(n, t, delta, k, p)
    end = default_timer()
    print "Setup took {0}".format(end - start)

    cs = []
    cTimes = []
    for sk in sks[1:]:
        start = default_timer()
        c = protocol.NoisyEnc(params, sk, 1, rand.randint(0, delta))        
        end = default_timer()
        cs.append(c)
        cTimes.append(end - start)

    for time in cTimes:
        print "NoisyEnc took {0}".format(time)
    
    for cVal in cs:
        print "NoisyEnc returned type {0}, value {1}".format(type(cVal),cVal)

    print "Sk[0] = {0}".format(sks[0].signed()) 
    prod = protocol.AggrDec(params, sks[0], 1, cs)
    print "Aggrdec: {0}".format(prod)
    runtime.shutdown()

def errorHandler(failure):
    print "Error handler: {0}".format(failure)

theRuntime = create_runtime(id, players, 1) # Not sure if the value 1 is correct here. Can't figure it out from documentation, it might need to be (n * t)
theRuntime.addCallback(doPsa)
theRuntime.addErrback(errorHandler)

reactor.run()