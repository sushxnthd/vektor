# V317 finite-buffer bank-port prospective result (2026-11-02)

## Provenance and scope

Frozen protocol: [FROZEN_FINITE_BANK_BACKPRESSURE_GATE_20261102.md](FROZEN_FINITE_BANK_BACKPRESSURE_GATE_20261102.md), committed **before implementation** at `35bdf710`. Simulator committed at `f005a961`; independent JSON-only audit at `bc0a33f2` (outcome-agnostic correction `4e2fdfd3`). Locally executed the committed-equivalent Python standard-library simulator and independently audited its JSON output. The full 15,384-byte local JSON has SHA-256 `191aec118e0346c90ccebddae33bac1d7315b0fc2ba57bfeffd01070943fbccf`. Hosted CI must independently reproduce the JSON and audit before claiming hosted validation.

This is a **synthetic** 24-versus-25 tile model, conditional on prior routed *controller* areas and a hypothetical area budget. The bank ports, FIFOs, eligibility, arbitration, tile replication and shared bandwidth are not measured from a GPU. Each tile has a 4-entry FIFO; the shared output has an 8-entry FIFO with same-cycle bypass; banks have one issue port each. FIFO heads retain bank IDs when stalled, introducing head-of-line (HOL) correlation. Three seeds (17,71,173), 2,048 warmup and 30,000 measured cycles each. The independent-head null law is evaluated without calling the event simulator.

## Prospective predictions and event results

| Regime | Banks | Shared cap | Pairwise eligibility q | Frozen independent-head ratio | Finite-buffer ratio (3 seeds) | Absolute error | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| W_ports | 32 | 32 | 1.00 | 1.02735253 | 1.02451506 | 0.00283748 | PASS |
| N_ports | 4 | 4 | 1.00 | 1.00025110 | 0.99981048 | 0.00044062 | PASS |
| R_eligibility | 32 | 32 | 0.85 | **0.91859780** | **0.93410560** | **0.01550780** | **FALSIFIED** |
| N_bandwidth | 32 | 12 | 1.00 | 1.00001452 | 1.00000278 | 0.00001174 | PASS |
| H_marginal | 32 | 32 | 0.95 | 0.99249186 | 0.99694916 | 0.00445730 | PASS |
| E_equal_resource (24/24) | 32 | 32 | 1.00 | 1.00000000 | 1.00000000 | 0 | PASS |

The **precommitted 0.015 absolute error criterion was exceeded** in R_eligibility, by 0.00050780. The independent-head law therefore **fails as a universal predictive boundary** for finite queued heads. Do not relax the threshold or recalibrate it on these results. The sign of the predicted loss remains correct (a 6.59% observed loss versus 8.14% predicted), but its magnitude fails the frozen criterion.

Three-seed measured ratios, in frozen seed order:

- W_ports: 1.02375085, 1.02409411, 1.02570021.
- N_ports: 1.00015982, 0.99998225, 0.99928938.
- R_eligibility: 0.93323458, 0.93354834, 0.93553388.
- N_bandwidth: 1.00000000, 1.00000833, 1.00000000.
- H_marginal: 0.99755434, 0.99583318, 0.99745996.
- E_equal_resource: 1.00000000 for every seed.

The 32-bank unconstrained *positive* result is only **2.45% synthetic throughput gain**, not the earlier unbanked 4.17% tile-count gain. Four-bank pressure and shared bandwidth both erase the benefit. Equal-resource control remains exactly 1.000x. At q=0.85, pairwise loses 6.59%.

## Backpressure and independent audit

The simulator explicitly records completed operations, bank arbitration stalls, rejected local arrivals, output stalls, and FIFO maxima. For seed 17 in W_ports, source/pairwise throughput is 16.24643/16.63230 ops/cycle, blocked attempted admissions 232,605/251,032, and bank stalls 232,607/251,031. For N_bandwidth, the same seed saturates 12.00000 ops/cycle in both variants; output stalls are 95,995/104,489 and blocked attempted admissions 360,000/390,000. These are real finite-buffer *model* backpressure counts, not hardware measurements.

The independent checker validates frozen inputs, separate occupancy-DP predictions, arithmetic, per-seed ratios, FIFO bounds, service ceilings, and conservation of admitted/completed/blocked operations up to finite initial/final storage. It does not import the simulator. Local audit: **PASS**, while preserving the R_eligibility scientific falsification.

Reproduction:
```bash
python3 research/v317/rtl/finite_bank_backpressure.py > finite_bank_results.json
python3 research/v317/rtl/audit_finite_bank_backpressure.py finite_bank_results.json
```

## Decision and next hard gate

**Retain V317 only as a routed controller-area optimization.** Kill any unconditional 25/24 throughput or universal independent-head boundary claim. The next scientific task is to derive a pre-outcome HOL-corrected predictive law and freeze unseen bank-skew, finite-depth, port-count and eligibility regimes before testing; an independently coded event checker should challenge it. More importantly, the actual physical gate is RF SRAM macro, datapath, wire/load and tile-level P&R with matched legal timing and equal-resource alternatives. These synthetic results do not establish real GPU IPC, power, integrated tile area, novel architecture, or RTX-5090 equivalence.
