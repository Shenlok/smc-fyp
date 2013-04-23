from viff.field import GF
import hashlib
import random
import math

def discrete_log_lambda(a, base, bounds, operation='*'):
    """
    Pollard Lambda algorithm for computing discrete logarithms. It uses
    only a logarithmic amount of memory. It's useful if you have
    bounds on the logarithm. If you are computing logarithms in a
    whole finite group, you should use Pollard Rho algorithm.
    INPUT:
    
    - a - a group element
    - base - a group element
    - bounds - a couple (lb,ub) representing the range where we look for a logarithm
    - operation - string: '+', '*' or 'other'
    - hash_function -- having an efficient hash function is critical for this algorithm

    OUTPUT: Returns an integer `n` such that `a=base^n` (or `a=n*base`)

    ALGORITHM: Pollard Lambda, if bounds are (lb,ub) it has time complexity
        O(sqrt(ub-lb)) and space complexity O(log(ub-lb))

    EXEMPLES::

        sage: F.<a> = GF(2^63)
        sage: discrete_log_lambda(a^1234567, a, (1200000,1250000))
        1234567

       sage: F.<a> = GF(37^5, 'a')
        sage: E = EllipticCurve(F, [1,1])
        sage: P=E.lift_x(a); P
        (a : 9*a^4 + 22*a^3 + 23*a^2 + 30 : 1)

        This will return a multiple of the order of P:
        sage: discrete_log_lambda(P.parent()(0), P, Hasse_bounds(F.order()), operation='+')
        69327408

        sage: K.<a> = GF(89**5) 
        sage: hs = lambda x: hash(x) + 15
        sage: discrete_log_lambda(a**(89**3 - 3), a, (89**2, 89**4), operation = '*', hash_function = hs)
        704966

    AUTHOR:
        -- Yann Laigle-Chapuy (2009-01-25)

    """
    def hash_function(v):
        #return long(hashlib.sha256(str(v.value)).hexdigest(), 16)
        #return hash(v) + 15
        return hash(v*v)

    def isqrt(v):
        return int(math.floor(math.sqrt(v.value)))

    from operator import mul, add, pow

    if operation == '*':
        mult = mul
        power = pow
    else:
        mult=add 
        power=mul 
   

    lb,ub = bounds
    if lb<0 or ub<lb:
        raise ValueError, "discrete_log_lambda() requires 0<=lb<=ub"

    # check for mutability
    mut = hasattr(base,'set_immutable')

    width = ub-lb
    N = isqrt(width)+1

    M = dict()
    for s in xrange(10): #to avoid infinite loops
        #random walk function setup
        k = 0
        while (2**k<N):
            r = random.SystemRandom().randrange(1,N)
            M[k] = (r , power(base,r))
            k += 1
        #first random walk
        H = power(base,ub.value)
        c = ub
        for i in xrange(N):
            if mut: H.set_immutable()
            r,e = M[hash_function(H)%k]
            H = mult(H,e)
            c += r
        if mut: H.set_immutable()
        mem=set([H])
        #second random walk
        H = a
        d=0
        while c-d >= lb:
            if mut: H.set_immutable()
            if ub > c-d and H in mem:
                return c-d
            r,e = M[hash_function(H)%k]
            H = mult(H,e)
            d += r

    raise ValueError, "Pollard Lambda failed to find a log"