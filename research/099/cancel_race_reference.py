#!/usr/bin/env python3
"""Exhaustive single-tag cancel/FINAL priority oracle; not sequential RTL proof."""
from itertools import product
import json

def evaluate(pending,live,cb_valid,cb_final,cancel,soft_reset):
    final=bool(cb_valid and cb_final)
    old_match=bool(final and pending and live)
    new_match=bool(old_match and not cancel)
    return (bool(old_match and not soft_reset),
            bool(new_match and not soft_reset),
            bool(final and not (old_match and not soft_reset)),
            bool(final and not (new_match and not soft_reset)),
            bool(pending and not final),
            bool(live and not final and not cancel and not soft_reset))

def main():
    n=old_fail=new_fail=diff=0
    for values in product((0,1),repeat=6):
        pending,live,cb_valid,cb_final,cancel,soft_reset=values
        old,new,old_stale,new_stale,pending_after,live_after=evaluate(*values)
        race=bool(pending and live and cb_valid and cb_final and cancel and not soft_reset)
        old_fail+=bool(race and old)
        new_fail+=bool(race and new)
        diff+=bool(old!=new)
        assert not (old and old_stale) and not (new and new_stale)
        n+=1
    assert (n,old_fail,new_fail,diff)==(64,1,0,1)
    print(json.dumps(dict(cases=n,baseline_cancel_wins_failures=old_fail,
        corrected_failures=new_fail,policy_differences=diff)))
if __name__=="__main__":main()
