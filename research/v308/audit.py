"""Independent bank-demand/accounting audit for V308 synthetic results.

Bank demand is recomputed directly from frozen source pairs, not read from the
candidate's grant log. The performance result itself is rerun deterministically.
"""
from collector import workload, experiment


def audit():
    result=experiment()
    checks=0
    for kind,group in result.items():
        gains=[]
        for row in group['rows']:
            trace=workload(kind,row['seed'],1200)
            demand=[sum(source==bank for pair in trace for source in pair) for bank in range(2)]
            assert sum(demand)==2400
            for mode,data in row['modes'].items():
                assert data['bank_reads']==demand,(kind,row['seed'],mode)
                assert data['reads']==2400 and data['completed']==1200
                assert data['cycles']>=max(demand)
                assert data['cycles']>=1200
                assert data['max_collectors']<=4
                checks+=6
            old=row['modes']['srpt']['cycles']
            new=row['modes']['completion']['cycles']
            gain=100*(old/new-1)
            assert abs(gain-row['completion_vs_srpt_pct'])<1e-10
            gains.append(gain)
            checks+=1
            if kind in ('all_cross','skew'):
                assert row['modes']['completion']['cycles']==max(demand)
                checks+=1
        assert abs(sum(gains)/len(gains)-group['mean_vs_srpt_pct'])<1e-10
        checks+=1
    print(f'PASS independent demand and accounting audit: {checks} checks')
    print('W1 gain vs SRPT = %.6f%% (required >=5%%)'%result['iid']['mean_vs_srpt_pct'])
    assert result['iid']['mean_vs_srpt_pct']<5
    assert abs(result['all_cross']['mean_vs_srpt_pct'])<=1
    print('V308 NO-GO; all-cross no-win control passes')


if __name__=='__main__':
    audit()
