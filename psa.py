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
        def __init__(self, Zp, g, sigma, delta, rand):
            self.g = g
            self.Zp = Zp
            self.sigma = sigma
            self.delta = delta # message space size (delta is used in the paper)
            self._hashes = {} # only temporary
            self.rand = rand
            
        
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
        
        
        if xbar < 0:
            multiplicative_inverse = pow(g, Zp.modulus - 2)
            assert (multiplicative_inverse * g) == 1
            gxbar = multiplicative_inverse**abs(xbar)
        else:
            gxbar = (g**(xbar))

        sk = sk.unsigned()
        if sk < 0:
            multiplicative_inverse = pow(H(t), Zp.modulus - 2) # attempt modular exponentiation with neg exponent by finding modular multiplicative inverse
            assert (multiplicative_inverse * H(t))== 1
            c = gxbar * (multiplicative_inverse**abs(sk))
        else:
            c = gxbar * H(t)**sk
        return (c, xbar)
        
    def AggrDec(self, params, sk, t, cs):
        H = params.H
        g = params.g
        delta = params.delta # size of the message space
        
        cprod = reduce(lambda x, y: x * y, cs, 1) # Get the product of all the ciphertexts
        sk = sk.unsigned()

        # as in NoisyEnc() re: pow with negative exponent
        if sk < 0:
            multiplicative_inverse = pow(H(t), params.Zp.modulus - 2)
            assert (multiplicative_inverse * H(t))== 1
            v = (multiplicative_inverse**abs(sk)) * cprod
        else:
            v = (H(t)**sk) * cprod
        
        '''print "V = {0}".format(v)
        print "Upper-bound on pollard-lambda: {0}".format(len(cs)*delta)
        try:
            x = discrete_log_lambda(v, g, (0, len(cs)*delta))
        except ValueError:
            print "Pollard-lambda failed to find log with standard operator, trying alternative"
            x = discrete_log_lambda(v, g, (0, len(cs)*delta), '+')
        '''

        # TODO: use Pollard's lambda algorithm
        # For the moment, use 'brute force'
        h = g
        for x in longrange(len(cs)*delta):
            if v == h:
                return x + 1
            h *= g
        
        return None


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
        Zp = GF(p)
        assert Zp(8).unsigned() == 8
        self.g = self._find_gen(Zp, q, rand)
        tmpsks = [0] * (n + 1)
        self.sks = []
        for sk in tmpsks:
            self.sks.append(Zp(sk))
        for i in range(1, n + 1):
            self.sks[i] = Zp(rand.randint(0, Zp.modulus))   # Is this correct, or should it be from [-modulus..modulus]
        self.sks[0] = -reduce(lambda x, y: x + y, self.sks[1:])
        assert sum(self.sks).unsigned() == 0

        return (self.Params(Zp, self.g, sigma, delta, rand), self.sks)

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
