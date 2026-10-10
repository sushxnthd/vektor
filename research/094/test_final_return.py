import unittest
from itertools import product
from final_return_model import run

class ProtocolTests(unittest.TestCase):
    def test_first_beat_aba(self):
        steps=[dict(offer=True,latency=1,copies=2,spacing=4),
               dict(offer=True,latency=4,copies=1),
               dict(offer=True,latency=4,copies=1),
               dict(offer=True,latency=4,copies=1)] + [dict(offer=False)]*10
        self.assertGreater(run(steps,tags=1,policy='first').metrics['false'],0)
        self.assertEqual(run(steps,tags=1,policy='final').metrics['false'],0)
    def test_duplicate_final_falsifies_contract(self):
        steps=[dict(offer=True,latency=1,copies=1,duplicate_final_delta=2)] + [dict(offer=True,latency=2,copies=1)]*8
        self.assertGreater(run(steps,tags=1,policy='final').metrics['false'],0)
    def test_soft_reset_retains_pending(self):
        steps=[dict(offer=True,latency=3,copies=3),dict(offer=True,soft_reset=True)] + [dict(offer=True)]*8
        m=run(steps,tags=1,policy='final')
        self.assertEqual(m.metrics['false'],0)
        self.assertEqual(m.metrics['correct'],1)
    def test_bounded_enumeration(self):
        checked=0
        for offers in product((False,True),repeat=5):
            for copies in product((1,2),repeat=5):
                for reset_step in (-1,0,2,4):
                    steps=[dict(offer=offers[i],copies=copies[i],latency=1+i%2,
                        soft_reset=i==reset_step,cancel_mask=i==3) for i in range(5)]
                    steps += [dict(offer=False)]*16
                    for width in (1,2):
                        m=run(steps,tags=2,width=width,policy='final')
                        self.assertEqual(m.metrics['false'],0)
                        checked+=1
        self.assertEqual(checked,8192)
if __name__=='__main__':unittest.main()
