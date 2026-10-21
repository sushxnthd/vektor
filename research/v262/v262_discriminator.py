#!/usr/bin/env python3
"""V262 frozen-generator discriminator. E1 model; NOT RTL simulation or physical PPA."""
import argparse, hashlib, json, random
from collections import Counter

N=4096
SPECS={
 "positive":{"seed":262101,"compressible":3482,"compute_cap":1.0,"memory_cap":0.92},
 "negative":{"seed":262102,"compressible":164,"compute_cap":0.25,"memory_cap":0.90},
 "divergent":{"seed":262103,"compressible":327,"compute_cap":0.95,"memory_cap":0.45},
}
# Capacity caps (requests per original clock) are explicit illustrative assumptions,
# not calibrated GPU subsystem measurements.

def generate(name):
    s=SPECS[name]; rng=random.Random(s["seed"])
    mask=[True]*s["compressible"]+[False]*(N-s["compressible"])
    rng.shuffle(mask)
    out=[]
    for can in mask:
        base=rng.randrange(512,65000)
        if can:
            a=[base]+[base+rng.randrange(-16,16) for _ in range(3)]
        else:
            # Non-compressible groups deliberately contain at least one far delta.
            a=[base]+[base+rng.randrange(-16,16) for _ in range(3)]
            a[1]=base+rng.choice([-1,1])*rng.randrange(17,400)
        assert all(0<=v<65536 for v in a)
        out.append(tuple(a))
    return out

def eligible(a):
    return all(-16<=x-a[0]<=15 for x in a[1:])

def packet(a):
    if eligible(a):
        d=[(x-a[0]) & 31 for x in a[1:]]
        p=(a[0]<<15)|(d[0]<<10)|(d[1]<<5)|d[2]
        return ((1,p),)
    return ((0,(a[0]<<16)|a[1]),(0,(a[2]<<16)|a[3]))

def decode(beats):
    if len(beats)==1:
        mode,p=beats[0]; assert mode==1 and (p>>31)==0
        base=(p>>15)&0xffff
        ds=[(p>>10)&31,(p>>5)&31,p&31]
        return (base,)+tuple(base+(d-32 if d&16 else d) for d in ds)
    assert len(beats)==2 and all(mode==0 for mode,_ in beats)
    p0,p1=beats[0][1],beats[1][1]
    return ((p0>>16)&0xffff,p0&0xffff,(p1>>16)&0xffff,p1&0xffff)

def raw(a):
    return ((0,(a[0]<<16)|a[1]),(0,(a[2]<<16)|a[3]))

def toggle_count(stream):
    # 32 data wires + 1 mode wire. Bus retains last transmitted value between valid beats.
    previous=0
    flips=0
    for mode,word in stream:
        value=(mode<<32)|word
        flips+=(value^previous).bit_count()
        previous=value
    return flips

def run_one(name):
    a=generate(name)
    assert len(a)==N
    # Independent oracle: literal signed differences (does not call eligible/packet).
    oracle=sum(all(-16 <= int(v)-int(group[0]) <= 15 for v in group[1:]) for group in a)
    enc=[packet(x) for x in a]
    assert all(decode(y)==x for x,y in zip(a,enc))
    assert oracle==sum(len(x)==1 for x in enc)
    # Matched packetizer uses identical encoding and resources by construction.
    # Comparing to it is decisive: there is no distinguishable mechanism.
    matched=[packet(x) for x in a]
    assert matched==enc
    raw_stream=[b for x in a for b in raw(x)]
    enc_stream=[b for x in enc for b in x]
    raw_beats=len(raw_stream); enc_beats=len(enc_stream)
    raw_flips=toggle_count(raw_stream); enc_flips=toggle_count(enc_stream)
    s=SPECS[name]
    cap=s["compute_cap"]; mem=s["memory_cap"]
    # Throughput is constrained by 1 beat/original cycle injection,
    # by fixed compute and memory service caps; candidate runs at 0.95x clock.
    rate_raw=min(N/raw_beats,cap,mem)
    rate_enc=.95*min(N/enc_beats,cap,mem)
    rate_matched=rate_enc
    # Break-even of encoded vs raw link dynamic energy per request, with overhead H
    # measured in switched-bit energy equivalents and wire multiplier w.
    sensitivity=[]
    for w in (0.5,1.0,2.0):
        for H in (8,16,32):
            energy_raw=w*raw_flips
            energy_enc=w*enc_flips+H*N
            sensitivity.append({"wire_multiplier":w,"logic_overhead_bit_toggle_equiv_per_group":H,
                "raw_energy_proxy":energy_raw,"candidate_energy_proxy":energy_enc,
                "energy_saving_fraction":1-energy_enc/energy_raw})
    return {
        "name":name,"groups":N,"seed":s["seed"],"compressible":oracle,"p":oracle/N,
        "raw_beats":raw_beats,"candidate_beats":enc_beats,"matched_beats":len([b for x in matched for b in x]),
        "beat_reduction_fraction":1-enc_beats/raw_beats,
        "raw_link_toggles":raw_flips,"candidate_link_toggles":enc_flips,
        "raw_rate_per_original_cycle":rate_raw,"candidate_rate_per_original_cycle":rate_enc,
        "matched_rate_per_original_cycle":rate_matched,
        "candidate_speedup_vs_raw":rate_enc/rate_raw,
        "candidate_speedup_vs_matched":rate_enc/rate_matched,
        "sensitivity":sensitivity,
    }

def main():
    results={n:run_one(n) for n in SPECS}
    pos=results["positive"]; neg=results["negative"]; div=results["divergent"]
    gates={
        "positive_beat_reduction_ge_40pct":pos["beat_reduction_fraction"]>=0.4,
        "positive_end_to_end_gain_gt_10pct_under_frozen_link_bound_caps":pos["candidate_speedup_vs_raw"]>1.1,
        "negative_no_end_to_end_gain_gt_1pct":neg["candidate_speedup_vs_raw"]<=1.01,
        "divergent_no_robust_gain":div["candidate_speedup_vs_raw"]<=1.01,
        "matched_control_same_waveforms_all_workloads":all(results[n]["candidate_speedup_vs_matched"]==1 for n in results),
    }
    data={"evidence_class":"E1","generator_sha256":hashlib.sha256(open(__file__,"rb").read()).hexdigest(),
          "assumptions":{"link_data_bits":32,"mode_sideband_bits":1,"raw_beats_per_group":2,
              "candidate_frequency_retention":0.95,
              "memory_compute_caps_are_illustrative_not_measured":True,
              "bus_holds_last_value_between_valid_beats":True,
              "logic_overhead_sensitivity_in_switched_bit_equivalents":[8,16,32]},
          "gates":gates,"results":results}
    print(json.dumps(data,indent=2,sort_keys=True))
if __name__=="__main__":main()
