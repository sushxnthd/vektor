# V177 ARCHITECTURE ledger

The immediate architectural decision is whether V153 cutset is viable at the real V-Tile issue/RF operand arrival boundary. V151 remains functional reference. V153 is not accepted solely on nominal slack.

**V156 recovery.** Original Yosys unsupported option was plumbing, not timing falsification; corrected run 38969084092 passed. V177 reuses the exact original V156 CI workflow on the V156 research branch and adds a real seven-point OpenSTA sweep after matched mapping/oracle regression, without editing restricted workflow files.

**Inputs/outputs.** Script: research/v177/run_arrival_sweep.sh; pinned mapped netlists: build/v156/*_mapped.v; pinned Liberty blob: 90e4afb274cfc6514c587c434c77903d554117d1; output: build/v156/arrival_sweep/{14 logs,results.json,validation.json}. GitHub workflow artifact preserves failed and passed runs.

**Decision.** If cutset fails 10 ns setup at plausible operand arrival, redesign operand staging / retiming, or retain V151 and prioritize dense bypass. If cutset remains faster, move to actual tile RF->FP32 integration and equal-area synthesis. This is a *gate*, not a GPU performance claim.

**Wildcard (10% effort).** Check path-class transitions in control/cutset at 3–5 ns for unexpected register-input reversals; do not promote without an architectural consequence.
