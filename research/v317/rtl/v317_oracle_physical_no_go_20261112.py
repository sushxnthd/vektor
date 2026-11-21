"""Necessary-condition screen for four-slot oracle under a restricted service-bound model.

Assumptions: identical offered batches; service throughput proportional to
mean grants per batch; no queue-order, occupancy, overlap or traffic feedback.
Under these assumptions the maximum throughput/area gain is R/(c*A),
where R is the unfair oracle/greedy service ratio, c is clock inflation,
and A is area inflation. This is NOT a universal GPU throughput bound.
Other bottlenecks or workload feedback invalidate the inference and require
explicit evaluation. Inputs are published synthetic ratios, not routed data.
"""
from fractions import Fraction as F

RATIOS = {
    'uniform_16_bank': F('1.001025'),
    'same_bank_70pct': F('1.002278'),
    'uniform_4_bank': F('1.046683'),
    'hot_bank_65pct': F('1.099869'),
    'constructed_head_blocker': F('1.500'),
    'disjoint_control': F('1.000'),
}

def restricted_gain(r, clock_inflation, area_inflation, occupancy=F(1)):
    assert r >= 1 and clock_inflation > 0 and area_inflation > 0
    assert 0 < occupancy <= 1
    return r * occupancy / (clock_inflation * area_inflation)

def test():
    for name, r in RATIOS.items():
        assert restricted_gain(r,F(1),F(1)) == r
        assert restricted_gain(r,r,F(1)) == 1
        assert restricted_gain(r,r+F(1,1000000),F(1)) < 1
        assert restricted_gain(r,F(1),r+F(1,1000000)) < 1
        assert restricted_gain(r,F(1),F(1),F(9,10)) <= r
        print(f'{name}: necessary c*A < {float(r):.6f}; headroom {float((r-1)*100):.4f}%')
    assert restricted_gain(RATIOS['uniform_16_bank'],F(101,100),F(1)) < 1
    assert restricted_gain(RATIOS['hot_bank_65pct'],F(101,100),F(105,100)) > 1
    print('PASS: exact-rational restricted-model falsification checks')

if __name__ == '__main__':
    test()
