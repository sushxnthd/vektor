#!/usr/bin/env python3
"""V309 full-corpus comparison of old conservative vs exact antichain bounds.

All evidence is conditional on an unverified historical tracer source.
No GPU traffic, cycle, area, timing or performance claims.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import io
import json
import tarfile
from pathlib import PurePosixPath
from format0_sector_envelope import format0_envelope,MAX_TOTAL_CHOICES
from sector_antichain_dp import exact_sector_extrema,selftest
from legacy_predicate_mask_provenance import address_tail,format1_sector_envelope
from v100_sass_profile import EXPECTED_SHA
from v100_trace_inventory import MAX_ARCHIVE,validate_name

DP_GLOBAL_TRANSITION_CAP=2_000_000
DP_ROW_TRANSITION_CAP=100_000
DP_ROW_STATE_CAP=3_000


def scan(path):
    with open(path,"rb") as f:
        blob=f.read(MAX_ARCHIVE+1)
    if len(blob)>MAX_ARCHIVE or hashlib.sha256(blob).hexdigest()!=EXPECTED_SHA:
        raise ValueError("untrusted archive bytes")
    apps=defaultdict(Counter)
    files=0
    remaining_old=MAX_TOTAL_CHOICES
    remaining_dp=DP_GLOBAL_TRANSITION_CAP
    with tarfile.open(fileobj=io.BytesIO(blob),mode="r:gz") as tar:
        for member in tar:
            validate_name(member.name)
            if member.isdev():
                raise ValueError("unsafe archive member")
            if not member.isfile() or not member.name.endswith(".traceg"):
                continue
            if member.size>2*1024**3:
                raise ValueError("oversized trace member")
            parts=PurePosixPath(member.name).parts
            if len(parts)<5:
                raise ValueError("unexpected trace path")
            files+=1
            acc=apps[parts[2]]
            stream=tar.extractfile(member)
            if stream is None:
                raise ValueError("unreadable trace")
            for line_no,raw in enumerate(stream,1):
                line=raw.decode("utf-8",errors="replace").strip()
                if not line or not line[0].isdigit():
                    continue
                try:
                    record=address_tail(line)
                    if record is None:
                        continue
                    mask,op,width,fmt,data=record
                    acc["global_proxy"]+=1
                    if fmt==1:
                        acc["format1"]+=1
                        base,stride=(int(t,0) for t in data)
                        old_lo,old_hi,_=format1_sector_envelope(mask,width,base,stride)
                        new_lo,new_hi=old_lo,old_hi
                    elif fmt==0:
                        acc["format0"]+=1
                        old_lo,old_hi,sharp,used,method=format0_envelope(
                            mask,width,data,remaining_old)
                        remaining_old-=used
                        new_lo,new_hi=old_lo,old_hi
                        if method=="conservative" and old_lo<old_hi:
                            acc["dp_eligible"]+=1
                            if remaining_dp<=0:
                                acc["dp_global_budget_exhausted"]+=1
                            else:
                                lo,hi,meta=exact_sector_extrema(
                                    mask,width,data,max_states=DP_ROW_STATE_CAP,
                                    max_transitions=min(DP_ROW_TRANSITION_CAP,remaining_dp))
                                remaining_dp-=meta["transitions"]
                                acc["dp_"+meta["status"]]+=1
                                acc["dp_transitions"]+=meta["transitions"]
                                if meta["status"]=="exact":
                                    if not (old_lo<=lo<=hi<=old_hi):
                                        raise AssertionError("DP not contained in conservative envelope")
                                    new_lo,new_hi=lo,hi
                                    acc["dp_sharpened_rows"]+=int((lo,hi)!=(old_lo,old_hi))
                                    acc["dp_newly_identified_rows"]+=int(lo==hi)
                                    acc["dp_exact_rows"]+=1
                    else:
                        raise ValueError("unsupported memory format")
                    acc["old_sector_lower"]+=old_lo
                    acc["old_sector_upper"]+=old_hi
                    acc["new_sector_lower"]+=new_lo
                    acc["new_sector_upper"]+=new_hi
                    if not (old_lo<=new_lo<=new_hi<=old_hi):
                        raise AssertionError("envelope containment violation")
                except (ValueError,IndexError,AssertionError) as exc:
                    raise ValueError(f"{member.name}:{line_no}: {exc}") from exc
    global_counts=Counter()
    for a in apps.values():
        global_counts.update(a)
    g=global_counts
    if files!=210 or g["global_proxy"]!=240465 or g["format0"]!=106728 or g["format1"]!=133737:
        raise AssertionError("frozen full-corpus conservation failed")
    if (g["old_sector_lower"],g["old_sector_upper"])!=(1580660,1595620):
        raise AssertionError("previous result not reproduced")
    if not (g["old_sector_lower"]<=g["new_sector_lower"]<=g["new_sector_upper"]<=g["old_sector_upper"]):
        raise AssertionError("global containment violation")
    return {
        "evidence_tier":"unverified_historical_tracer_source_conditional_NOT_GPU_transactions",
        "producer_identity_verified":False,"archive_sha256":EXPECTED_SHA,
        "trace_files":files,"global":dict(g),
        "applications":{k:dict(v) for k,v in sorted(apps.items())},
        "budgets":{"old_mask_choices":MAX_TOTAL_CHOICES,"dp_global_transitions":DP_GLOBAL_TRANSITION_CAP,
                   "dp_row_transitions":DP_ROW_TRANSITION_CAP,"dp_row_states":DP_ROW_STATE_CAP},
        "interpretation":["No actual hardware bottleneck established",
                          "Rodinia families are not prospective unseen workloads",
                          "No hardware mechanism promoted; retired mechanisms stay retired",
                          "Not measured GPU traffic, cache misses, stalls, cycles, timing or power"]
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("archive",nargs="?")
    p.add_argument("--selftest",action="store_true")
    args=p.parse_args()
    if args.selftest:
        print(json.dumps(selftest(),sort_keys=True))
    if args.archive:
        print(json.dumps(scan(args.archive),indent=2,sort_keys=True))
    elif not args.selftest:
        p.error("archive required")
