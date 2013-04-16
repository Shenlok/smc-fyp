from optparse import OptionParser
import viff.reactor
viff.reactor.install()
from twisted.internet import reactor
from psa import PSA
from pprint import pprint
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
sys.stdout = open("logs/log-{0}-rass.txt".format(id), "w")

protocol = PSA()

n = len(players)

t = 0.33

rand = random.SystemRandom()

def sub(x,y):
    return x - y

def doRass(runtime):
    s = rand.randint(0, 100)

    print "I am player {0}, my s is: {1}".format(runtime.id, s)
    
    num = 2*((n+5)/6)

    if runtime.id == 1: # We are the coordinator
        rs = []
        for i in range(1, n+1):
            if i < 3:
                rs.append(rand.random())
            else:
                rs.append(s - reduce(sub, rs[:i-1]))
        
        pprint(rs)
        # Do sending of shares here

    

    runtime.shutdown()

def errorHandler(failure):
    print "Error handler: {0}".format(failure)

theRuntime = create_runtime(id, players, 1)
theRuntime.addCallback(doRass)
theRuntime.addErrback(errorHandler)

reactor.run()