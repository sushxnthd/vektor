import sys, unittest, random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from wb_cancel_aba_089 import Model, trial

class TestCancellation(unittest.TestCase):
    def test_wrapping_tag_counterexample(self):
        m={p:Model(2,6,p) for p in ('unsafe','quarantine','boundary')}
        for t in range(7):
            for obj in m.values():obj.step(t<5,1<=t<=4,6)
        self.assertEqual(m['unsafe'].false,1)
        self.assertEqual(m['quarantine'].false,0)
        self.assertEqual(m['boundary'].false,0)
    def test_bounded_callbacks(self):
        for bits in (1,2,3,4):
            for D in (2,3,6,9):
                for seed in range(10):
                    result=trial(bits,D,.6,seed,512)
                    for p in ('quarantine','boundary','oracle'):
                        self.assertEqual(result[p]['false'],0,(bits,D,seed,p))
    def test_violated_bound(self):
        result=trial(1,2,.9,1200,20000,True)
        self.assertGreater(result['quarantine']['false'],0)
    def test_no_stalls_with_enough_tags(self):
        for D in range(2,17):
            for bits in range(1,6):
                m=Model(bits,D,'boundary')
                for _ in range(256):m.step(True,True,D)
                if (1<<bits)>=D:self.assertEqual(m.stalls,0,(D,bits))
    def test_inflight_tag_uniqueness(self):
        rng=random.Random(889)
        m=Model(2,6,'boundary')
        for _ in range(4096):
            m.step(rng.random()<.97,rng.random()<.6,rng.randint(1,6))
            if m.active:
                self.assertFalse(any(tag==m.active[1] and uid!=m.active[0]
                    for events in m.events.values() for uid,tag in events))
if __name__=='__main__':unittest.main()
