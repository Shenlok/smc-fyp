from psa import PSA
import cProfile
import sys
import time
import random

p = PSA()

n = 4

t = 0.33

delta = 100

k = 1024

rand = random.SystemRandom()

start = time.clock()
params, sks = p.setup(n, t, delta, k)
end = time.clock()

print "Setup took {0}".format(end - start)

start = time.clock()
p.NoisyEnc(params, sks[1], 1, rand.randint(0, delta - 1))
end = time.clock()

print "NoisyEnc took {0}".format(end - start)

sys.stdin.readline()