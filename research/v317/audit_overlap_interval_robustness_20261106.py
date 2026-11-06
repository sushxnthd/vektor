"""Conservative overlap-uncertainty bound; hypothetical seconds per useful operation, not GPU measurements."""
from dataclasses import dataclass
from itertools import product

@dataclass(frozen=True)
class Interval:
    low: float
    high: float
    def __post_init__(self):
        assert 0 <= self.low <= self.high

def time(c, m, o):
    assert c > 0 and m > 0 and 0 <= o <= 1
    return c + m - o * min(c, m)

def bounds(bc, bm, bo, cc, cm, co):
    assert bo.high <= 1 and co.high <= 1
    return (time(bc.low,bm.low,bo.high)/time(cc.high,cm.high,co.low),
            time(bc.high,bm.high,bo.low)/time(cc.low,cm.low,co.high))

def test():
    a = (Interval(.95,1.05),Interval(.38,.42),Interval(.95,1),
         Interval(.88,.92),Interval(.38,.42),Interval(.70,.90))
    lo,hi=bounds(*a)
    assert lo < 1 < hi
    for vals in product(*[(i.low,i.high) for i in a]):
        r=time(*vals[:3])/time(*vals[3:])
        assert lo-1e-12 <= r <= hi+1e-12
    # Memory service alone is worse than the entire baseline: robust no-win.
    no=bounds(Interval(1,1),Interval(.4,.4),Interval(1,1),
              Interval(.9,.9),Interval(1.2,1.2),Interval(0,1))
    assert no[1] < 1
    for k in (.001,1,1e6):
        f=lambda i:Interval(i.low*k,i.high*k)
        x=bounds(f(a[0]),f(a[1]),a[2],f(a[3]),f(a[4]),a[5])
        assert abs(x[0]-lo)<1e-12 and abs(x[1]-hi)<1e-12
    print("PASS 64 vertices, 3 scale controls; uncertain",lo,hi,"robust no-win",no)

if __name__=="__main__":
    test()
