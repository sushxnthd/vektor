#!/usr/bin/env python3
"""Frozen holdout parameters. Do not execute before physicality gate."""
SEEDS={'positive':269101,'no_win':269102,'divergent':269103}
CONFIGS={
 'positive':dict(T=20000,offered=.85,slow_frac=.5,blocked=.75,fast_burst=True),
 'no_win':dict(T=20000,offered=.60,slow_frac=.1,blocked=0.,fast_burst=False),
 'divergent':dict(T=20000,offered=.80,slow_frac=.35,blocked=.50,fast_burst=True)}
def config(name):return dict(seed=SEEDS[name],**CONFIGS[name])
if __name__=='__main__':raise SystemExit('Holdouts frozen and unopened')
