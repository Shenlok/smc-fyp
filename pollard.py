from viff.field import GF
import hashlib
import random
import math

def longrange(stop):
    i = 0
    while i <= stop:
        yield i
        i += 1

def isqrt(v):
    return int(math.floor(math.sqrt(v)))

def random_element(field):
    return field(random.randint(0, field.modulus))

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
        return hash(v) + 15
        #return hash(v*v)



    from operator import mul, add, pow

    
    if operation == '*':
        mult = mul
        power = pow
    else:
        mult=add 
        power=mul 
   
    Zp = GF(base.modulus)
    lb,ub = bounds
    if hasattr(lb, 'value'):
        lb = lb.value
    if hasattr(ub, 'value'):
        ub = ub.value
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
        H = power(base,ub)
        c = ub
        for i in longrange(N):
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

def discrete_log_rho(a, base, ord=None, operation='*', hash_function=hash):
    """ 
    Pollard Rho algorithm for computing discrete logarithm in cyclic 
    group of prime order.
    If the group order is very small it falls back to the baby step giant step
    algorithm.

    INPUT:

    - a - a group element 
    - base - a group element 
    - ord - the order of base or None, in this case we try to compute it 
    - operation - a string  (default: '*')  wether we are in an
       additive group or a multiplicative one 
    - hash_function - having an efficient hash function is critical
       for this algorithm (see examples) 

    OUTPUT: return an integer $n$ such that `a=base^n` (or `a=n*base`) 

    ALGORITHM: Pollard rho for discrete logarithm, adapted from the article of Edlyn Teske, 
    'A space efficient algorithm for group structure computation' 

    EXAMPLES::

        sage: F.<a> = GF(2^13) 
        sage: g = F.gen() 
        sage: discrete_log_rho(g^1234, g) 
        1234 
    
        sage: F.<a> = GF(37^5, 'a') 
        sage: E = EllipticCurve(F, [1,1]) 
        sage: G = 3*31*2^4*E.lift_x(a) 
        sage: discrete_log_rho(12345*G, G, ord=46591, operation='+') 
        12345 
    
    It also works with matrices::

        sage: A = matrix(GF(50021),[[10577,23999,28893],[14601,41019,30188],[3081,736,27092]])
        sage: discrete_log_rho(A^1234567, A)
        1234567

    Beware, the order must be prime::
    
        sage: I = IntegerModRing(171980)
        sage: discrete_log_rho(I(2), I(3))
        Traceback (most recent call last):
        ...
        ValueError: for Pollard rho algorithm the order of the group must be prime

    If it fails to find a suitable logarithm, it raises a ``ValueError``::

        sage: I = IntegerModRing(171980)
        sage: discrete_log_rho(I(31002),I(15501))
        Traceback (most recent call last):
        ...
        ValueError: Pollard rho algorithm failed to find a logarithm

    The main limitation on the hash function is that we don't want to have
    `hash(x*y) = hash(x)+hash(y)`::

        sage: I = IntegerModRing(next_prime(2^23))
        sage: def test():
        ...       try:
        ...            discrete_log_rho(I(123456),I(1),operation='+')
        ...       except StandardError:
        ...            print "FAILURE"
        sage: test() # random failure
        FAILURE

    If this happens, we can provide a better hash function::

        sage: discrete_log_rho(I(123456),I(1),operation='+', hash_function=lambda x: hash(x*x))
        123456

    AUTHOR:

    - Yann Laigle-Chapuy (2009-09-05) 
    
    """ 
    #from sage.rings.integer import Integer
    from gmpy import mpz
    #from sage.rings.finite_rings.integer_mod_ring import IntegerModRing 
    from operator import mul, add, pow 
    
    # should be reasonable choices
    partition_size=20
    memory_size=4 

    if operation == '+': 
        mult=add 
        power=mul 
        if ord==None: 
            ord=base.additive_order() 
    elif operation == '*':
        mult=mul 
        power=pow 
        if ord==None: 
            ord=base.multiplicative_order() 
    else:
        raise(ValueError, "unknown operation")

    ord = mpz(ord)

    if not ord.is_prime():
        raise ValueError,"for Pollard rho algorithm the order of the group must be prime"

    # check if we need to set immutable before hashing
    mut = hasattr(base,'set_immutable')
         
    isqrtord=isqrt(ord)
    
    '''if isqrtord < partition_size: #setup to costly, use bsgs 
        return bsgs(base,a, bounds=(0,ord), operation=operation) '''
    
    reset_bound = 8*isqrtord # we take some margin
         
    I=GF(ord)
    
    for s in xrange(10): # to avoid infinite loops
        # random walk function setup 
        m=[random_element(I) for i in xrange(partition_size)]
        n=[random_element(I) for i in xrange(partition_size)] 
        M=[mult(power(base,mpz(m[i].value)),power(a,mpz(n[i].value))) for i in xrange(partition_size)]
         
        ax = random_element(I) 
        x = power(base,mpz(ax.value))
        if mut:
            x.set_immutable()

        bx = I(0) 
         
        sigma=[(0,None)]*memory_size 
        H={} # memory 
        i0=0 
        nextsigma = 0 
        for i in longrange(reset_bound): 
                    #random walk, we need an efficient hash 
            s=hash_function(x) % partition_size 
            (x,ax,bx) = (mult(M[s],x), ax+m[s], bx+n[s]) 
            if mut:
                x.set_immutable()
            # look for collisions
            if x in H:
                ay,by=H[x]
                if bx == by:
                    break 
                else: 
                    res = mpz(((ay-ax)/(bx-by)).value)
                    if power(base,res) == a:
                        return res
                    else:
                        break
            # should we remember this value?
            elif i >= nextsigma: 
                if sigma[i0][1] is not None: 
                    H.pop(sigma[i0][1])
                sigma[i0]=(i,x)
                i0 = (i0+1) % memory_size 
                nextsigma = 3*sigma[i0][0] #3 seems a good choice 
                H[x]=(ax,bx)
         
    raise ValueError, "Pollard rho algorithm failed to find a logarithm"
