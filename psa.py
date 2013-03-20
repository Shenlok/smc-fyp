import random

# G - A cyclic group of prime order p
G = []

# n - number of parties
n = 100

# m - size of message range (message values lie between 0 and (m-1) inclusive)
m = 20

# t - Threshold, a value in the interval [0, 1] representing the fraction of parties that are corrupt
t = random.random()

# H : Z - Hash function modelled as a random oracle
def H():


def NoisyEnc(param, ski, t, xbar):


# From Section 5.2 of paper
def setup():
    # Trusted dealer chooses a random generator 'g' (in G) and n+1 random secrets s0,s1...sn (Integers up to p)
    # s0 + s1 + ... sn = 0
    # Secret keys sk0,sk1..skn
    # sk[0] is known as the capability
    # sk[i] is obtained by participant i
    sk = []
    s = []
