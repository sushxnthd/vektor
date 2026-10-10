class Arbiter:
    def __init__(self, sources=4, guard=16):
        self.n = sources
        self.guard = guard
        self.rr = 0
        self.wait = [0] * sources

    def step(self, valid, final, sink_ready):
        active = [i for i in range(self.n) if valid[i]]
        overdue = [i for i in active if self.wait[i] >= self.guard]
        if overdue:
            selected = min(overdue, key=lambda i: (-self.wait[i], (i-self.rr)%self.n))
        else:
            finals = [i for i in active if final[i]]
            pool = finals if finals else active
            selected = min(pool, key=lambda i: (i-self.rr)%self.n) if pool else None
        grant = selected if sink_ready else None
        self.wait = [0 if not valid[i] or i == grant else min(65535, self.wait[i]+1) for i in range(self.n)]
        if grant is not None:
            self.rr = (grant+1)%self.n
        return grant

if __name__ == '__main__':
    a=Arbiter()
    seen=set()
    for _ in range(512):
        seen.add(a.step([1,1,1,1],[1,0,0,0],True))
    assert seen=={0,1,2,3}
    print('PASS four-source fairness under continuous demand')
