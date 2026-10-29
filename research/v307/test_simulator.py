"""Independent brute-force legality and conservation checks."""
import itertools, unittest
from simulator import legal, advance, next_pressure, program, simulate, select

class Tests(unittest.TestCase):
    def test_legality_independent(self):
        n=0
        for masks in itertools.product((3,5,6,9,10,12),repeat=4):
            queues=tuple((m,) for m in masks)
            head=(0,)*4
            actual=set(legal(head,queues))
            expected=set()
            for k in range(5):
                for ids in itertools.combinations(range(4),k):
                    if k>3: continue
                    used=0
                    for w in ids:
                        if used & masks[w]: break
                        used|=masks[w]
                    else: expected.add(sum(1<<w for w in ids))
            self.assertEqual(actual,expected)
            n+=1
        self.assertEqual(n,1296)
    def test_pressure(self):
        self.assertEqual(next_pressure((0,0),((3,),(3,))),2)
        self.assertEqual(next_pressure((0,0),((3,),(12,))),0)
    def test_conservation(self):
        for regime in ('W1','N1','N2'):
            for seed in (0,1,2):
                q=program(seed,regime)
                for p in ('max_now','pressure','future_tie'):
                    d=simulate(q,p)
                    self.assertEqual(d['issued'],240)
                    self.assertGreaterEqual(d['cycles'],80)
    def test_selection(self):
        q=program(0,'W1');head=(0,)*5
        for p in ('max_now','pressure','future_tie'):
            self.assertIn(select(head,q,p),legal(head,q))

if __name__=='__main__': unittest.main()
