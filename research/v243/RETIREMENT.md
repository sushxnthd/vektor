# V243 retirement, 2026-10-20

Four-input, one-output last-fragment-first response arbitration failed against a shortest-remaining-fragments control with identical response capacity, count metadata and collector budget.

Exhaustive 2,500-case oracle: 0 wins, 244 ties, 2,256 losses on total warp completion cycles. Positive holdout seed 243101: 0% throughput gain; no mean-latency win versus age-first. Negative seed 243102: 0% throughput gain as predicted.

Saturated response conservation bound: warp completions per cycle cannot exceed response bandwidth divided by average response fragments per warp. No PPA evidence was obtained. Do not integrate into the tile. V153/V156 remain electrically disqualified.

Prior art: MeDiC (PACT 2015), DOI 10.1109/PACT.2015.38; DRAM latency divergence (SC 2014), DOI 10.1109/SC.2014.16.

Complete local reproducibility archive includes the event simulator, full RTL and independent checker. Remote publication of long source files was rejected by connector safety checks.
