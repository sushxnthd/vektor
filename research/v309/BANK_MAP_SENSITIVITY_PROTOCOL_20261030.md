# V309: frozen V100 bank-map sensitivity protocol (2026-10-30)

**Frozen before the new full-corpus bank-map sweep.** This is an exploratory identifiability falsification, not a hardware mechanism, measured RF stall, unseen workload prediction, or GPU speedup. The original modulo-bank full-corpus results were already inspected. No application in this same archive is a prospective holdout.

## Immutable source
Purdue 2020 Tesla V100 Rodinia SASS archive `rodinia_2.0-ft.tgz`, SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`. Include all 11 application families, 210 trace files, and all active rows. Fail on digest mismatch, unsafe tar members, empty data, or >1% unsupported rows.

## Precommitted model and strongest control
Count each distinct register source only once (free intra-instruction broadcast). Assume R255 bypass, explicitly unverified. Compare hypothetical maps `modB: r % B` and `xorB: (r XOR (r >> log2(B))) % B` at B=2,4,8. Neither map is claimed to be the physical V100 mapping. For isolated instruction i, define `L_i(B,P)=max_b ceil(n_ib/P)` for n_ib unique sources assigned to bank b, with L=0 if no sources. Record `max(0,L_i-1)` as extra isolated read-service cycles at P=1 and P=2. This is **not** a stall, latency, IPC, or throughput estimate. Two ports are a resource sensitivity, not an equal-area baseline.

## Frozen falsification gates
1. Extra isolated read cycles cannot increase with P=2 relative to P=1; under modulo maps they cannot increase as B grows 2->4->8. Any violation fails the run.
2. Compute exact pairwise workload-ranking inversions between modulo and XOR mappings, using extra P=1 read cycles per active instruction, separately for each B. Ties do not count. Any inversion falsifies a mapping-independent workload ranking. Zero inversions establish stability only under these two models, not physical validity.
3. If modeled serialization disappears with two ports, do not attribute a necessary scheduler benefit to the one-port conflict incidence.
4. No hardware promotion without independently matched counters or validated simulation, actual bank/collector configuration, equal-resource controls, prospective workload regimes, RTL/synthesis/electrical validation.

## Independent audit
Reconcile global/per-family metrics, frozen SHA, 11 families, 3,937,565 active rows, monotonicity, and six corrupted-report mutations. Preserve JSON and checker output in hosted CI. No Blackwell or RTX 5090 transfer claim.
