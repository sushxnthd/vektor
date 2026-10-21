#!/usr/bin/env python3
"""Frozen unseen workload parameters. Do not execute before physicality gate."""
import json,random
SEEDS={'positive':269101,'no_win':269102,'divergent':269103}
CONFIGS={'positive':dict(T=20000,offered=0.85,slow_frac=0.5,blocked=0.75,fast_burst=True),
         'no_win':dict(T=20000,offered=0.60,slow_frac=0.1,blocked=0.0,fast_burst=False),
         'divergent':dict(T=20000,offered=0.80,slow_frac=0.35,blocked=0.50,fast_burst=True)}
def config(name):
    assert name in SEEDS
    return dict(seed=SEEDS[name],**CONFIGS[name])
if __name__=='__main__':
    raise SystemExit('Holdouts frozen, intentionally unopened until RTL/electrical checks.')
