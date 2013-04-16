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

delta = 100

k = 1024

rand = random.SystemRandom()

def doPsa(runtime):
    print "I am player {0}".format(runtime.id)
    start = default_timer()
    params, sks = protocol.setup(n, t, delta, k, p)
    end = default_timer()
    print "Setup took {0}".format(end - start)

    print "Params types: {0}, {1}, {2}, {3}, {4}".format(type(params.delta),type(params.g.value),type(params.rand),type(params.sigma),type(params.Zp))

    start = default_timer()
    c = protocol.NoisyEnc(params, sks[1], 1, rand.randint(0, delta - 1))
    end = default_timer()

    print "NoisyEnc took {0}".format(end - start)
    print "NoisyEnc returned type {0}, value {1}".format(type(c),c)
    runtime.shutdown()

def errorHandler(failure):
    print "Error handler: {0}".format(failure)

theRuntime = create_runtime(id, players, 1) # Not sure if the value 1 is correct here. Can't figure it out from documentation, it might need to be (n * t)
theRuntime.addCallback(doPsa)
theRuntime.addErrback(errorHandler)

reactor.run()