"""Independent policy sensitivity for synthetic three-FIFO bank scheduling.

A fixed-priority failure does not establish an advantage over inexpensive
rotating-priority controls. Enumerates the same 4096 frozen instances and
compares fixed order, cyclic order, and a clairvoyant dynamic-programming
upper bound. No hardware timing or GPU IPC claims.
"""
from functools import lru_cache
from itertools import product, combinations

HORIZON = 3

def run(queues, mode):
    queues = tuple(tuple(q) for q in queues)
    @lru_cache(None)
    def dp(t, pos):
        if t == HORIZON: return 0
        eligible = [i for i in range(3) if pos[i] < 2 and queues[i][pos[i]][1] <= t]
        if mode != 'oracle':
            order = sorted(eligible, key=lambda i: (i - (t if mode == 'rotate' else 0)) % 3)
            chosen, banks = [], set()
            for i in order:
                bank = queues[i][pos[i]][0]
                if bank not in banks and len(chosen) < 2:
                    chosen.append(i); banks.add(bank)
            nxt = tuple(pos[i] + (i in chosen) for i in range(3))
            return len(chosen) + dp(t+1,nxt)
        best = dp(t+1,pos)
        for size in (1,2):
            for chosen in combinations(eligible,size):
                banks = [queues[i][pos[i]][0] for i in chosen]
                if len(set(banks)) != size: continue
                nxt = tuple(pos[i] + (i in chosen) for i in range(3))
                best = max(best, size + dp(t+1,nxt))
        return best
    return dp(0,(0,0,0))

def audit():
    counts = {'cases':0,'fixed_below_oracle':0,'rotate_below_oracle':0,'rotate_beats_fixed':0,'fixed_beats_rotate':0,'rotate_equals_oracle':0}
    examples = {}
    for config in product(product(range(2),range(2)),repeat=6):
        q = tuple(tuple(config[2*i:2*i+2]) for i in range(3))
        f,r,o = (run(q,mode) for mode in ('fixed','rotate','oracle'))
        assert 0 <= f <= o <= 6 and 0 <= r <= o
        counts['cases'] += 1
        for key, condition in [('fixed_below_oracle',f<o),('rotate_below_oracle',r<o),('rotate_beats_fixed',r>f),('fixed_beats_rotate',f>r),('rotate_equals_oracle',r==o)]:
            counts[key] += condition
            if condition and key not in examples: examples[key] = (q,f,r,o)
    assert counts == {'cases':4096,'fixed_below_oracle':1056,'rotate_below_oracle':912,'rotate_beats_fixed':624,'fixed_beats_rotate':448,'rotate_equals_oracle':3184}, counts
    print(counts)
    print('first_examples',examples)

if __name__=='__main__': audit()
