from viff.field import GF
from viff.util import find_prime
from gmpy import mpz
from operator import mul
import random


class PSA:
    _hashes = {}

    def _H(self, Zp, x):
        if x not in self._hashes:
            self._hashes[x] = Zp.random_element()
        return self._hashes[x]

    def NoisyEnc(self, param, sk, t, xbar):
        c = (g^xbar) * self._H(t)^sk
        return c
        
    def AggrDec(self, param, sk, t, cs):
        cprod = reduce(mul, cs, 1) # Get the product of all the ciphertexts
        v = (self._H(t)^sk) * cprod
        return v


    # k is the security parameter
    def setup(self, k, n):
        q, p = self._find_p(k) 
        Zp = GF(p)
        self.g = self._find_gen(Zp, q)
        self.sks = [0] * (n + 1)
        for i in range(1, n + 1):
            self.sks[i] = Zp(random.randrange(Zp.modulus))   # Here I replaced Zp.random_element() as this function doesn't seem to exist on FieldElement's
        self.sks[0] = -sum(self.sks[1:])

        return (self.g, self.sks)

    def _find_p(self, k):
        q = find_random_prime(k)
        while not mpz(2*q + 1).is_prime:
            q = find_random_prime(k)
        return (q, 2*q + 1)


    def _find_gen(self, Zp, q):
        g = Zp(random.randrange(Zp.modulus))
        while g^2 == 1 or g**q == 1:
            g = Zp(random.randrange(Zp.modulus))
        return g
