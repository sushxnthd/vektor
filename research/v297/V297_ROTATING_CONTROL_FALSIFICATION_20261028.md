# V297 adversarial fair-rotation control: strong-baseline falsification (2026-10-28)

**Prospective protocol:** `V297_ROTATING_CONTROL_PREREG_20261028.md` was committed at `837d3cef` before the control was implemented or the fresh-seed results were opened. Eight new seeds, 100,000 synthetic cycles each, six original frozen regimes. This test is **not RTL, matched physical synthesis, or GPU throughput**.

The stronger comparator is an independent serial greedy controller with deterministic priority rotation (0-1-2, 1-2-0, 2-0-1), the **same three requests, two issue slots and two read ports per bank**. It does not conditionally compute a second pair grant. Logic area, critical-path cost, fairness and power are not matched.

| Frozen regime | Fixed-priority greedy | Fair-rotation greedy | V297 rescue | V297 minus rotation |
|---|---:|---:|---:|---:|
| iid 40% blocker mixture | 1.599775 | 1.866648 | 1.885475 | +0.0188275 |
| uniform16 | 1.999015 | 1.999023 | 1.999920 | +0.0008975 |
| all-hot | 1 | 1 | 1 | 0 |
| single issue port | 1 | 1 | 1 | 0 |
| single ready request | 1 | 1 | 1 | 0 |
| 37-cycle bursts | 1.499400 | 1.832813 | 1.756632 | **-0.0761800** |

**Major narrowing:** The earlier +17.88% V297 result was against fixed priority. Against a much stronger, simple, fair rotating baseline, the iid mixture advantage is only **+1.009%** in synthetic admission. In the bursty stress regime, V297 is **4.156% worse** than rotating greedy at equal clock. This negative transfer is preserved.

### Physical kill boundary
For the iid mixture, the V297 clock must be at least `1.8666475 / 1.885475 = 0.99001445` of the rotating serial clock, **assuming identical completed-work behavior**. Thus an additional clock slowdown of only ~0.999% relative to rotation erases the remaining offered-request admission advantage. For bursts, V297 would need **4.337% higher clock frequency** than rotation just to match admissions; no such advantage is established. Extra area, energy, queue latency, fairness overhead or wire cost may further worsen V297.

### Research decision
**Reject any claim that V297 offers a robust 17.88% architecture-level win.** The 17.88% fixed-priority figure remains a valid synthetic observation but is not a strong-baseline result. V297 is provisionally retained only for one bounded matched RTL synthesis/physical kill test against *rotating serial*, not merely fixed priority. If it cannot preserve the ~1% conditional iid advantage under equal physical resources and persistent-queue throughput, retire V297 immediately. This is not a demonstrated novel scheduling technique; bank-aware scheduling and round-robin arbitration are established prior art.

Reproduce: `node research/v297/v297_rotating_control.js`. Machine-readable results: `V297_ROTATING_CONTROL_RESULTS_20261028.json`. The original preregistration and holdouts remain unchanged. Kernellum PR #119 untouched.
