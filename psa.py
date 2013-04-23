from viff.field import GF
from viff.util import find_random_prime
from gmpy import mpz
from operator import mul
import random
import hashlib
import math
from pollard import discrete_log_lambda

def longrange(stop):
    i = 0
    while i <= stop:
        yield i
        i += 1

class PSA:
    class Params:
        def __init__(self, Zp, g, sigma, delta, rand, Zq):
            self.g = g
            self.Zp = Zp
            self.sigma = sigma
            self.delta = delta # message space size (delta is used in the paper)
            self._hashes = {} # only temporary
            self.rand = rand
            self.Zq = Zq
            
        
        def H(self, x):
            if x not in self._hashes:
                # we haven't cached our hash for this x, calculate + cache it
                hs = []
                h = hashlib.sha256()
                h.update(str(x))
                hs.append(h.hexdigest())
                for x in range(0,3):
                    h = hashlib.sha256()
                    h.update(hs[x])
                    hs.append(h.hexdigest())
                hx = long("".join(hs), 16)
                while hx > self.Zp.modulus:
                    hx = hx >> 1
                self._hashes[x] = self.Zp(hx)
            return self._hashes[x]
   
    # params is the public parameters, an instance of class Params
    # sk is our personal secret key
    # t is the timestep for which we are computing this encrypted input
    # x is our plaintext, unmodified input
    def NoisyEnc(self, params, sk, t, x):
        g = params.g
        H = params.H
        Zp = params.Zp
        sigma = params.sigma
        rand = params.rand

        #r = round(rand.gauss(0, sigma))
        r = 0
        xbar = Zp(x + r).unsigned()
        
        gxbar = (g**(xbar))
        c = gxbar * (H(t)**sk)
        return (c, xbar)
        
    def AggrDec(self, params, sk, t, cs):
        H = params.H
        g = params.g
        Zp = params.Zp
        delta = params.delta # size of the message space
        
        cprod = reduce(lambda x, y: x * y, cs, 1) # Get the product of all the ciphertexts

        v = (H(t)**sk) * cprod
        
        print "V = {0}".format(v)
        print "Upper-bound on pollard-lambda: {0}".format(Zp(len(cs)*delta))
        try:
            assert type(v) == type(g)
            x = discrete_log_lambda(v, g, (Zp(0), Zp(len(cs)*delta)))
        except ValueError:
            print "Pollard-lambda failed to find log with standard operator, trying alternative"
            x = discrete_log_lambda(v, g, (Zp(0), Zp(len(cs)*delta)), '+')
        return x
        '''
        # TODO: use Pollard's lambda algorithm
        # For the moment, use 'brute force'
        h = g
        for x in longrange(len(cs)*delta):
            if v == h:
                return x + 1
            h *= g
        
        return None'''
        

    # n is the number of parties.
    # t is the collusion tolerance (in [0, 1]).
    # delta is the size of the message space (i.e. range is {0, ..., delta - 1}).
    # k is the security parameter.
    # p is an optional prime p to use in place of searching for an appropriate one.
    def setup(self, n, t, delta, k, p = 0):
        # TODO: assertions
        rand = random.SystemRandom()
        sigma = delta / math.sqrt(n*(1 - t))
        if p == 0: 
            q, p = self._find_p(k)
        else:
            q = (p - 1) / 2 
        
        assert delta < q
        assert n*delta < q
        
        Zp = GF(p)
        Zq = GF(q)
        assert Zp(8).unsigned() == 8
        self.g = self._find_gen(Zp, q, rand)**2
        tmpsks = [0] * (n + 1)
        self.sks = []
        for sk in tmpsks:
            self.sks.append(Zq(sk))
        for i in range(1, n + 1):
            self.sks[i] = Zq(rand.randint(0, Zq.modulus))
        self.sks[0] = -reduce(lambda x, y: x + y, self.sks[1:])
        assert sum(self.sks).unsigned() == 0
        self.sks = map(lambda x: x.unsigned(), self.sks)

        return (self.Params(Zp, self.g, sigma, delta, rand, Zq), self.sks)

    def _find_p(self, k):
        q = find_random_prime(k)
        while not mpz(2*q + 1).is_prime():
            q = find_random_prime(k)
        return (q, 2*q + 1)


    def _find_gen(self, Zp, q, rand):
        g = Zp(rand.randrange(Zp.modulus))
        while g^2 == 1 or g**q == 1:
            g = Zp(rand.randrange(Zp.modulus))
        return g
