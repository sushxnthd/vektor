import itertools
import unittest
from collector import Slot, legal_grants, select, grant_score, run, workload

class CollectorTests(unittest.TestCase):
    def test_exhaustive_grant_legality(self):
        cases=0
        for n in range(1,5):
            for pattern in itertools.product([(0,),(1,),(0,0),(0,1),(1,1)],repeat=n):
                slots=[Slot(i,i,list(p)) for i,p in enumerate(pattern)]
                for policy in ['oldest','srpt','completion']:
                    grant=select(slots,policy)
                    self.assertIn(grant,list(legal_grants(slots)))
                    self.assertEqual(grant_score(slots,grant,policy),max(map(lambda g:grant_score(slots,g,policy),legal_grants(slots))))
                    cases+=1
        self.assertEqual(cases,2340)

    def test_conservation_and_capacity(self):
        for kind in ['iid','skew','alternating','mixed','all_cross']:
            for seed in [1,2,3]:
                for policy in ['oldest','srpt','completion']:
                    out=run(workload(kind,seed,80),policy)
                    self.assertEqual(out['reads'],160)
                    self.assertEqual(out['completed'],80)
                    self.assertLessEqual(out['max_collectors'],4)
                    self.assertTrue(all(x<=out['cycles'] for x in out['bank_reads']))

    def test_low_load_negative(self):
        trace=workload('iid',5,100)
        out=[run(trace,p,arrival_interval=6)['cycles'] for p in ['oldest','srpt','completion']]
        self.assertEqual(len(set(out)),1)

if __name__=='__main__':unittest.main()
