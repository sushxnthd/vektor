import unittest
from joint_cost import Config,grouped,trace,run
from sweep import discovery
class JointCostTests(unittest.TestCase):
    def test_lane_conservation(self):
        for pattern in ['coherent','balanced','minority','four_path','random']:
            c=Config(pattern=pattern,seed=71); lanes=trace(c)
            for compact in (False,True):
                groups=grouped(lanes,compact)
                self.assertEqual(sorted((x.warp,x.lane) for g in groups for x in g),
                                 sorted((x.warp,x.lane) for x in lanes))
                self.assertTrue(all(len(g)<=32 for g in groups))
    def test_oracle_and_reads(self):
        for c in discovery():
            x=run(c)
            self.assertLessEqual(x['totals']['oracle'],x['totals']['ipdom'])
            self.assertLessEqual(x['totals']['oracle'],x['totals']['dwf'])
            self.assertEqual(x['windows'][0]['base']['rf_reads'],x['windows'][0]['compacted']['rf_reads'])
    def test_bank_ports_monotone(self):
        for p in ['balanced','minority','four_path']:
            for mem in (0,1):
                a=run(Config(pattern=p,rf_ports=2,memory_stride=mem))
                b=run(Config(pattern=p,rf_ports=8,memory_stride=mem))
                for key in ['ipdom','dwf']:
                    self.assertLessEqual(b['totals'][key],a['totals'][key])
    def test_coherent_setup_control(self):
        for length in (1,4,16,32):
            x=run(Config(pattern='coherent',length=length,setup=4))
            self.assertGreater(x['totals']['dwf'],x['totals']['ipdom'])
    def test_positive_negative_control(self):
        a=run(Config(pattern='balanced',length=16,rf_ports=2,migration_bw=8))
        b=run(Config(pattern='balanced',length=16,rf_ports=8,migration_bw=8))
        self.assertGreater(a['totals']['dwf'],a['totals']['ipdom'])
        self.assertLess(b['totals']['dwf'],b['totals']['ipdom'])
    def test_mapping_sensitivity(self):
        a=run(Config(pattern='four_path',length=16,rf_ports=2,migration_bw=8,bank_scheme='linear'))
        b=run(Config(pattern='four_path',length=16,rf_ports=2,migration_bw=8,bank_scheme='lane'))
        self.assertGreater(a['speedup'],1)
        self.assertLess(b['speedup'],1)
if __name__=='__main__':unittest.main()
