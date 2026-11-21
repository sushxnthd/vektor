# Hosted rotating-scan structural audit — 2026-11-20 UTC

## Reproducibility checkpoint

- Lineage: V296/V317; V287 historical only.
- Existing research branch: `research/v317-sass-provenance-gate`; existing draft PR: #34.
- GitHub Actions workflow: `.github/workflows/v317-periodic-conservation.yml`.
- Hosted run: https://github.com/sushxnthd/vektor/actions/runs/44728292456
- Status/conclusion: completed/success (connector read-back).
- Job: `independent-periodic-audit`; step 8, `Audit frozen rotating-scan implementation classification`, completed/success; step 9, `Report frozen rotating-scan audit source digests`, completed/success.
- Other existing periodic and paired-trace checks (steps 4 and 6) also completed/success.
- The workflow checks out repository source and executes `python -B research/v317/rtl/rotating_scan_structural_audit_20261120.py`.
- Source blob SHA of audit read back from GitHub: `46771b31a63e4e68749345ae88ded08894e64f23`; workflow blob SHA: `79c40c714464b3e399f7366635f809b84963fb21`. These are Git blob IDs, **not** SHA-256 digests.

## Interpretation

The hosted structural assertion suite passed for the committed candidate: its scan orders are (0,1,2,3) and (0,2,1,3), both starting at slot 0. It is an alternating middle-slot priority policy, **not** a true four-way rotating-priority scheduler. This is a structural source audit, not independent performance replication or a proof that every rotating-priority policy fails.

The prior development throughput ratio (geometric mean 0.999935x versus compact greedy) pertains only to this frozen implementation. The candidate remains rejected. Do not open the reserved holdout seeds or promote this candidate to RTL/physical implementation. Earlier protected-oracle throughput, area, and electrical failures remain binding.

No new synthesis, routing, SRAM, wire-load sensitivity, power estimate, or GPU IPC was obtained by this CI success. No RTX-5090-equivalence claim is supported. Keep the default-branch 2026-11-20 activity entry unchanged (one checkpoint per UTC day).
