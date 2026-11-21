#!/usr/bin/env python3
"""V296 mapped-decoder inversion: independent exact-rational falsification.
Source: research/v296/BANK_DECODE_MAPPED_AND_CANDIDATE_PRECTS_RESULTS_20261026.json
This is mapped-only evidence; never interpret it as routed timing or GPU speed.
"""
from fractions import Fraction as Q

def q(x): return Q(str(x))

def assess(baseline_pairwise, baseline_serial, decoded_pairwise, decoded_serial):
    bp, bs, dp, ds = map(q, (baseline_pairwise, baseline_serial, decoded_pairwise, decoded_serial))
    if min(bp, bs, dp, ds) <= 0: raise ValueError("positive mapped areas required")
    baseline_saving = (bs-bp)/bs
    decoded_saving = (ds-dp)/ds
    pairwise_decoder_tax = dp-bp
    serial_decoder_tax = ds-bs
    # At fixed decoded-serial area, pairwise must save at least this much area
    # before any area-reinvestment hypothesis becomes feasible.
    required_reduction = max(Q(0),dp-ds)
    return dict(baseline_saving=baseline_saving, decoded_saving=decoded_saving,
                pairwise_decoder_tax=pairwise_decoder_tax, serial_decoder_tax=serial_decoder_tax,
                decoder_tax_differential=pairwise_decoder_tax-serial_decoder_tax,
                required_pairwise_area_reduction=required_reduction,
                required_pairwise_area_reduction_pct=required_reduction/dp,
                area_reinvestment_survives=dp<ds)

def self_test():
    r=assess("9519.608","9902.648","10426.402","10143.112")
    assert r["baseline_saving"]>0 and r["decoded_saving"]<0
    assert r["required_pairwise_area_reduction"]==q("283.290")
    assert r["decoder_tax_differential"]==q("666.330")
    assert not r["area_reinvestment_survives"]
    assert assess(1,2,1,2)["area_reinvestment_survives"]
    assert not assess(1,2,3,2)["area_reinvestment_survives"]
    print("PASS: mapped-only V296 decoder inversion; pairwise needs 283.290 um^2 (%.4f%%) area removal before parity" % (float(r["required_pairwise_area_reduction_pct"]*100)))
    print("No physical timing, electrical signoff, workload throughput, or GPU claim.")
if __name__=="__main__": self_test()
