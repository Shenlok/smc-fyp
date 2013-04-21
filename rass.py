from random import SystemRandom



class RASS:
    def __init__(self, id, n, s, t = 0.33, b = 32):
        self.id = id
        self.n = n
        self.s = s
        self.t = t
        self.b = b
        self.maxVal = (2**b) - 1
        self.rand = SystemRandom()
        self.numShares = 2*((n+5)/6)

    def modAdd(self, x, y):
        return (x + y) % self.maxVal
                    
    def gen_shares(self):
        rs = []
        for i in range(1, self.numShares + 2):
            if i < self.numShares or (self.id == 1 and i < self.numShares + 1):
                rs.append(self.rand.randint(0, self.maxVal))
            elif i == self.numShares or (self.id == 1 and i == self.numShares + 1):
                rs.append(self.s - reduce(self.modAdd, rs[:i-1]))
        self.rs = rs
        return rs