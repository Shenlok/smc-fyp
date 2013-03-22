from viff.field import GF
from viff.util import find_prime
import random


class PSA:
    _hashes = {}

    def _H(self, Zp, x):
        if x not in self._hashes:
            self._hashes[x] = Zp.random_element()
        return self._hashes[x]

    def NoisyEnc(self, param, sk, t, xbar):
        pass
        


    # k is the security parameter
    def setup(self, k, n):
        p = find_prime(2**k) # Don't believe this is random, but that said i'm not sure that's an issue
        Zp = GF(p)
        g = self._find_gen(Zp)
        sks = [0] * (n + 1)
        for i in range(1, n + 1):
            sks[i] = Zp(random.randrange(Zp.modulus))   # Here I replaced Zp.random_element() as this function doesn't seem to exist on FieldElement's
        sks[0] = -sum(sks[1:])

        return (g, sks)


    def _find_gen(self, Zp):
        found = False
        while not found:
            g = Zp(random.randrange(Zp.modulus))    # As above in sk generation
            if g.multiplicative_order() == Zp.order() - 1:  # Here neither g.multiplicative_order() nor Zp.order() seem to exist, and i'm not sure how to replace/implement them myself.
                found = True
        return found
