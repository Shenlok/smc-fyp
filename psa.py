from viff.field import GF
from viff.util import find_prime
from gmpy import mpz
from operator import mul
import random


# TODO: use a CSPRNG. Python's PRNG as we are using here is not suitable
# for cryptographic purposes
class PSA:
    class Params:
        def __init__(self, Zp, g, sigma, delta, rand):
            self.g = g
            self.Zp = Zp
            self.sigma = sigma
            self.delta = delta # message space size (delta is used in the paper)
            self._hashes = {} # only temporary
            self.rand = rand
            
        # This is only temporary/
        # TODO: use cryptographic hash function
        def H(self, x):
            if x not in self._hashes:
                self._hashes[x] = self.Zp(random.randrange(self.Zp.modulus))
            return self._hashes[x]
   

    def NoisyEnc(self, params, sk, t, x):
        g = params.g
        H = params.H
        Zp = params.Zp
        sigma = params.sigma

        r = round(random.gauss(0, sigma))
        xbar = Zp(x + r)
        
        c = (g**xbar) * H(t)**sk
        return c
        
    def AggrDec(self, params, sk, t, cs):
        H = params.H
        g = params.g
        delta = params.delta # size of the message space
        
        cprod = reduce(mul, cs, 1) # Get the product of all the ciphertexts
        v = (H(t)**sk) * cprod
        
        # TODO: use Pollard's lambda algorithm
        # For the moment, use 'brute force'
        h = g
        for x in range(delta):
            if v == h:
                return x
            h *= g
        
        return None


    # n is the number of parties
    # t is the collusion tolerance (in [0, 1]) - might want to use different letter
    # delta is the size of the message space (i.e. range is {0, ..., delta - 1})
    # k is the security parameter
    def setup(self, n, t, delta, k):
        # TODO: assertions
        rand = random.SystemRandom()
        sigma = delta / sqrt(n*(1 - t)) 
        q, p = self._find_p(k) 
        Zp = GF(p)
        self.g = self._find_gen(Zp, q, rand)
        self.sks = [0] * (n + 1)
        for i in range(1, n + 1):
            self.sks[i] = Zp(rand.randrange(Zp.modulus))   # Here I replaced Zp.random_element() as this function doesn't seem to exist on FieldElement's
        self.sks[0] = -sum(self.sks[1:])

        return (Params(Zp, self.g, sigma, delta, rand), self.sks)

    def _find_p(self, k):
        q = find_random_prime(k)
        while not mpz(2*q + 1).is_prime:
            q = find_random_prime(k)
        return (q, 2*q + 1)


    def _find_gen(self, Zp, q, rand):
        g = Zp(rand.randrange(Zp.modulus))
        while g^2 == 1 or g**q == 1:
            g = Zp(rand.randrange(Zp.modulus))
        return g
