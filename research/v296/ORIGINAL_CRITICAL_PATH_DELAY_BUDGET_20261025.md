# V296 original extracted setup-path delay-budget falsification (2026-10-25)

**Evidence tier:** original matched post-CTS, detailed-route, OpenRCX-extracted OpenSTA critical paths. This is an independent read-only analysis of **one original worst setup path per contestant**, not signoff or a repaired design. [Original run](https://github.com/sushxnthd/vektor/actions/runs/40203738175).

## SHA-locked reproduction

Download v296-in-situ-path-pairwise and v296-in-situ-path-serial_onehot from original run 40203738175. Their respective artifact ZIP SHA-256 values are 239a648829c41f5cd0229ec1ca6663463ca2a253d9186321bb476869223e640e and d755641eba65a4b89c36f1226ae23e55ce647b390dc910e649d157360d538815. Run:

    python3 research/v296/path_delay_decomposition.py pairwise.zip serial.zip

The independent executable checks original ZIP hashes, endpoint identities, timing-report cumulative arithmetic, slack against the physical audit, and that neither contestant closed hold/cap. A tampered artifact fails closed. Its output is also frozen in ORIGINAL_CRITICAL_PATH_DELAY_BUDGET_RESULTS.json.

## Matched original critical-path observations

| Extracted setup-path quantity | V296 | Serial one-hot |
|---|---:|---:|
| Worst setup slack (ns) | -1.047895 | -1.859922 |
| Launch clock network (ns) | 0.247074 | 0.222353 |
| Clock-to-Q increment (ns) | 0.159392 | 0.172698 |
| Functional-cell-attributed increments (ns) | 3.178597 | 3.691466 |
| Buffer-attributed increments (ns) | 1.155046 | 1.452727 |
| Data arrival (ns) | 4.740173 | 5.539272 |
| Data required (ns) | 3.692278 | 3.679350 |
| Functional cells on worst path | 58 | 65 |
| Physical buffers on worst path | 36 | 44 |
| Largest contiguous buffer chain | 9 cells / 0.249885 ns | 20 cells / 0.524563 ns |
| Slack recovery to +50 ps (ns) | **1.097895** | **1.909922** |

**Accounting caveat:** The reported incremental OpenSTA arrival times are attributed to cell-output pins and can include upstream interconnect propagation. They are **not an intrinsic gate-delay/wire-delay decomposition**. Names such as wire*, max_cap*, rebuffer*, load_slew* refer to physically inserted buffers. They cannot be deleted while holding loads and parasitics fixed. Six-decimal printed increments accumulate minor rounding. The two original critical paths have different launch/capture endpoints and cannot be interpreted as a matched causal per-gate ablation.

## Necessary repair boundary for the original fixed paths

Let B be the sum of buffer-attributed increments, R = 0.050 ns - original setup slack, and f be a **hypothetical upper bound** on the fraction of B saved without changing launch/capture clock timing. Then additional nonbuffer-path recovery must be at least **max(0, R - fB)**. This is only a necessary accounting bound for the original path, never sufficient for timing/electrical closure: repair changes loading, skew, critical-path ranking, area, hold and cap.

| Hypothetical buffer-increment reduction | V296 minimum additional nonbuffer recovery | Serial minimum additional nonbuffer recovery |
|---|---:|---:|
| 0% | 1.097895 ns | 1.909922 ns |
| 25% | 0.809134 ns | 1.546740 ns |
| 50% | **0.520372 ns** | **1.183559 ns** |
| 75% | 0.231611 ns | 0.820377 ns |
| 100% (physically impossible ideal) | 0 ns | **0.457195 ns** |

**Falsification:** Buffer-only cleanup cannot close the original serial critical path even if all its buffer-attributed delay vanished. Even if half of V296's buffer-attributed delay could disappear, >0.52 ns of nonbuffer path recovery is still necessary. This rules out treating simple buffer tuning as an adequate matched repair strategy. The serial baseline must receive independent scheduler-cone optimization rather than being left deliberately weak.

The observed V296 setup-slack lead is 0.812027 ns, of which 0.297681 ns is associated with differences in buffer-attributed increments and 0.526145 ns with nonbuffer-attributed increments; launch/capture clock differences account for the remaining offset. These are descriptive, not causal, and are not a measured Fmax advantage.

## Next physical experiment and kill gate

Preserve the frozen 3.5 ns clock, +50 ps setup requirement, matched physical constraints and the original negative evidence. Preregister a scheduler-to-executed-data **logic-topology** repair and an independently optimized equal-consumed-area serial control before new routing. Require independent RTL equivalence, detailed route, extracted setup/hold, cap/slew, area, power proxies and workload throughput with frozen win/no-win regimes. A surviving gain must remain after control optimization, critical-path reranking, wire/load sensitivity and bandwidth limits; otherwise kill the speedup claim.

**Limits:** Only one worst path per architecture; no intrinsic cell/net delay split, no matched repaired physical closure, no silicon power, no measured tile-level GPU speedup. Both original integrated designs fail the 3.5 ns physical gate, including three capacitance violations and negative hold slack. V296 remains the sole provisional mechanism, V287 retired, and no RTX-5090-equivalence claim is supported.
