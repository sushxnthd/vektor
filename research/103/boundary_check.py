"""Vektor-103 controlled lower-bound reproducer; not a GPU simulator."""
from math import ceil

def bound(issue_width, ports, compact):
    warps, lanes, paths, banks, length = 8, 32, 2, 16, 16
    groups = warps if compact else warps * paths
    requests_per_bank = warps * lanes * 2 // banks
    issue = ceil(groups / issue_width)
    rf = ceil(requests_per_bank / ports)
    startup = 8 if compact else 0
    return max(issue, rf) * length + startup

def test_boundary():
    assert (bound(1,4,False), bound(1,4,True)) == (256,136)
    assert (bound(4,4,False), bound(4,4,True)) == (128,136)
    assert bound(1,4,True) < bound(1,4,False)
    assert bound(4,4,True) > bound(4,4,False)

if __name__ == "__main__":
    test_boundary()
    for width in (1,2,4,8):
        print(width, bound(width,4,False), bound(width,4,True))
