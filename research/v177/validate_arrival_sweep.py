#!/usr/bin/env python3
"""V184 fail-closed independent validator for the V156/V176 input-arrival sweep."""
import json, math, sys
from pathlib import Path
EXPECTED=(0.05,0.5,1.,2.,3.,4.,5.)

def validate(sweep_path,baseline_path):
    sweep=json.loads(Path(sweep_path).read_text())
    baseline=json.loads(Path(baseline_path).read_text())
    rows=sweep["rows"]
    if len(rows)!=len(EXPECTED): raise ValueError("expected seven points")
    for a,b in (("clock_period_ns","clock_period_ns"),("library_git_blob","library_git_blob"),
                ("input_slew_ns","input_transition_ns"),("output_delay_ns","output_delay_ns"),
                ("output_load_library_units","output_load_library_units")):
        if sweep[a]!=baseline[b]: raise ValueError(f"mismatched constraint {a}")
    for i,(x,row) in enumerate(zip(EXPECTED,rows)):
        if not math.isclose(row["input_delay_ns"],x,abs_tol=1e-8): raise ValueError("wrong sweep point")
        for mode in ("control","cutset"):
            z=row[mode]; d=z["constrained_period_minus_slack_ns"]; s=z["slack_ns"]
            if not all(math.isfinite(v) for v in (d,s)): raise ValueError("nonfinite timing")
            if not math.isclose(d,10-s,abs_tol=0.001): raise ValueError("delay/slack mismatch")
            if z["path_class"] not in ("input-to-register","register-to-register","other"): raise ValueError("unknown path class")
            if not z["startpoint"] or not z["endpoint"]: raise ValueError("missing endpoints")
            if i:
                prev=rows[i-1][mode]["constrained_period_minus_slack_ns"]
                dx=x-EXPECTED[i-1]
                if d < prev-0.03 or d > prev+dx+0.03: raise ValueError("monotonic or Lipschitz violation")
        c=row["control"]["constrained_period_minus_slack_ns"]
        d=row["cutset"]["constrained_period_minus_slack_ns"]
        a=sweep["area_units"]["control"]; b=sweep["area_units"]["cutset"]
        if min(a,b,c,d)<=0: raise ValueError("nonpositive metric")
        if not math.isclose(row["cutset_timing_gain_pct"],100*(1-d/c),abs_tol=.02): raise ValueError("timing gain mismatch")
        if not math.isclose(row["cutset_area_delay_gain_pct"],100*(1-b*d/(a*c)),abs_tol=.02): raise ValueError("area-delay gain mismatch")
    for mode in ("control","cutset"):
        z=rows[0][mode]; b=baseline["candidates"][mode]
        if not math.isclose(z["slack_ns"],b["worst_reported_path_slack_ns"],abs_tol=.03): raise ValueError("baseline mismatch "+mode)
    return {"passed":True,"points":len(rows),"evidence_class":"mapped, unplaced OpenSTA; not physical PPA",
            "timing_advantage_points":[r["input_delay_ns"] for r in rows if r["cutset_timing_gain_pct"]>0],
            "area_delay_advantage_points":[r["input_delay_ns"] for r in rows if r["cutset_area_delay_gate"]]}

if __name__=="__main__":
    print(json.dumps(validate(sys.argv[1],sys.argv[2]),indent=2))
