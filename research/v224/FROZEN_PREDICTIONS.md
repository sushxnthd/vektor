# V224 frozen predictions (2026-10-19; before evaluation)

Mechanism: zero-sector suppression on four 32-bit return sectors, with a one-flit header carrying the sector-valid mask. Only this one mechanism is under test.

Matched control: whole-line-zero elision, same 32-bit link, same header, FIFO entries, credits, completion width, and link clock. Both return all four 32-bit words losslessly.

Law (ideal link-limited packet service): F_base = 1 + 4*(1-P_all_zero); F_candidate = 1 + E[number_nonzero_sectors]. For completion/credit limits C and B/L, predicted speedup = min(1/F_candidate,C,B/L) / min(1/F_base,C,B/L) - 1. Real hardware overhead and timing must be separately checked.

Frozen positive holdout: seed 22419, 4096 lines, each line has exactly two zero and two nonzero sectors; link-limited, C=1 packet/cycle, B/L>=1 packet/cycle. Predict 5/3-1=+66.67% ideal line throughput; require >=+60% software modeled, measured link-flit count 3/line.

Frozen negative holdout: seed 22420, 4096 lines, all four sectors nonzero; same capacities. Predict 0% throughput gain, both use 5 flits/line; tolerance 0.1%.

Completion-bound holdout: same positive data but C=0.1 packets/cycle. Predict no throughput gain; both 0.1 packets/cycle (if B/L>=0.1). This must be tested separately.

Falsify if lossless reconstruction fails, if control can match the gain with <= area/timing under same resources, if post-synthesis timing violates target or electrical max-cap/slew, or if realistic wire/loading makes area-energy-throughput tradeoff unacceptable. No RTX 5090 comparison.

Prior art: GPU memory compression and zero-value compression are well established; V224 is an engineering qualification experiment, not a novelty claim.
