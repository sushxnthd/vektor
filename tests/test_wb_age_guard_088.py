"""Vektor-088: CI checks the committed compact executable."""
from experiments.wb_age_guard_088 import Calendar, experiment

def test_cross_latency_starvation_and_protection():
    r=experiment([1,2,3,4])
    assert r["baseline"]==[1,1,1,4096]
    assert r["triggered"]==[205,205,205,3484]
    assert min(r["static"])>=1024

def test_single_class_throughput_cost():
    r=experiment([2,2,2,2],valid=[1,0,0,0])
    assert sum(r["static"])<sum(r["baseline"])
    assert r["triggered"]==r["baseline"]

def test_safety_and_bounded_progress():
    for age in (4,8,16,32,64):
        r=experiment([1,2,3,4],cycles=1024,age=age)
        assert all(x>0 for x in r["triggered"])
    m=Calendar("triggered")
    for _ in range(100):
        grant,due=m.step([1]*4,[1,2,3,4])
        assert due<=1 and sum(grant)<=4
