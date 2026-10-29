"""Independent conservation oracle for V301 scoreboard response experiments."""
import itertools
from collections import defaultdict
from scoreboard import run


def reference(events):
    expected = defaultdict(int)
    for _, warp, epoch, sector in events:
        expected[(warp, epoch)] |= sector
    return expected


def exhaustive():
    # Independent expected update count and OR masks, including epoch aliases.
    alphabet = [(w,e,1 << s) for w in range(2) for e in range(2) for s in range(2)]
    checks = 0
    for seq in itertools.product(alphabet, repeat=3):
        events = [(i//2, *v) for i,v in enumerate(seq)]
        oracle = reference(events)
        assert len(oracle) <= 3
        for policy in ('fifo','ingress','queue_merge','set2','set4','banked'):
            out = run(events,policy,capacity=4,ingress=2,return_digest=True)
            assert out['digest'] == oracle
            assert out['arrivals'] == len(events)
            assert out['cycles'] >= 2
            checks += 1
    print(f'independent exhaustive event conservation: {checks} runs passed')

if __name__ == '__main__':
    exhaustive()
