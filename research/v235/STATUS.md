# V235 direct-comparison bank arbiter

Evidence class: independent functional-model check only. 2,048,576 cases, zero mismatches. See results/functional.json.

Proposed change: compare source-bank identities directly instead of updating bank occupancy masks. Baseline is main-branch RF bank arbiter, with identical 16 banks, four issue slots and two reads per bank.

This is not a validated physical or architectural improvement. RTL simulation, synthesis, electrical max-cap/slew, STA, matched area, power, and workload evidence are missing. V153/V156 remain electrically disqualified. No integrated-tile change.

Executable source publication was rejected by repository safety checks. Preserve that failure and do not infer a pass from baseline CI. One further physical-validation attempt maximum; otherwise retire V235.
