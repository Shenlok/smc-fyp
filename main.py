from psa import PSA
import cProfile
import sys
import time
import random

protocol = PSA()

n = 4

p = 8210367885679168766758950738484631605814497398518690371786648569002948704711364117378465988124313755366044696642284768924819556022676696987591359662994541674288334772534600049590413961300804080139388895971566128327100549100994100446988248682535394236326347178554088960814072469643139825048533231637837365239

t = 0.33

delta = 100

k = 1024

rand = random.SystemRandom()

start = time.clock()
params, sks = protocol.setup(n, t, delta, k, p)
end = time.clock()

print "Safe prime found: {0}".format(params.Zp.modulus)
print "Setup took {0}".format(end - start)

start = time.clock()
protocol.NoisyEnc(params, sks[1], 1, rand.randint(0, delta - 1))
end = time.clock()

print "NoisyEnc took {0}".format(end - start)

sys.stdin.readline()