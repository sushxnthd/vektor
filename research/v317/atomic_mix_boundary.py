"""Exact independent-arrival atomic-bank compatibility boundary and holdout check.

Two single-port banks, two output slots, one-cycle unit jobs. Each request
independently draws mask 1 with probability (1-a)/2, mask 2 likewise, or
mask 3 with probability a. Two requests arrive together and must be served
in that cycle (no buffering). A feasible dual issue requires masks 1 and 2.
The exact expected maximum useful completions is 1+(1-a)^2/2.
This is a zero-queue upper bound, NOT a GPU throughput prediction.
"""
from fractions import Fraction
from itertools import product
import json

MASKS=(1,2,3)

def predicted(a):
    return 1+(1-a)**2/2

def exact(a):
    probs={1:(1-a)/2,2:(1-a)/2,3:a}
    return sum(probs[x]*probs[y]*(2 if not x&y else 1)
               for x,y in product(MASKS,repeat=2))

def audit():
    # Freeze train and unseen rational mixture grid before computing outcomes.
    train=[Fraction(i,8) for i in range(9)]
    holdout=[Fraction(i,16) for i in range(1,16,2)]
    results=[]
    for split,grid in [('train',train),('holdout',holdout)]:
        for a in grid:
            p=predicted(a)
            e=exact(a)
            assert p==e
            results.append({'split':split,'atomic_fraction':str(a),
                            'expected_completions':str(e),
                            'dual_issue_probability':str(e-1)})
    assert predicted(Fraction(0))==Fraction(3,2)
    assert predicted(Fraction(1))==1
    # Equal-resource strongest comparator is optimal same-cycle mask matching.
    # It already achieves this ceiling; no scheduling-hardware win is possible
    # in this restricted model without adding buffering or changing resources.
    return {'evidence_tier':'EXACT_ANALYTIC_SYNTHETIC_NOT_PHYSICAL',
            'law':'E[completions]=1+(1-a)^2/2; a=P(atomic two-bank request)',
            'holdout_max_absolute_error':'0',
            'train_points':len(train),'holdout_points':len(holdout),
            'results':results,
            'falsification':'A proposed scheduler cannot exceed this same-cycle optimum under identical two-bank/two-slot constraints.',
            'limitations':'IID symmetric bank draws; exactly two simultaneous requests; no queues, timing, wiring, RTL, area, power, or real workload evidence.'}

if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
