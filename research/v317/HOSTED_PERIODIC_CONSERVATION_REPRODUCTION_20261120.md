# Hosted byte-identical periodic conservation audit — 2026-11-20

## Reproduction and persistence gate

- Existing research branch: `research/v317-sass-provenance-gate`; draft PR #34 remains open.
- Workflow source commit: `4fd4ad7da88fa97b8c0cb44ef42305c7f953ab6d`.
- GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/44671962297
- Workflow: `.github/workflows/v317-periodic-conservation.yml`.
- Job: `independent-periodic-audit` (job ID `136074765037`), completed **success**.
- `actions/checkout@v4` completed successfully; `actions/setup-python@v5` completed successfully.
- Step `Run checked-out byte-identical source` completed **success**, executing `python -B research/v317/rtl/independent_periodic_conservation_audit_20261120.py`.
- Step `Report source SHA-256 for independent audit` completed **success**. The digest itself was not retrieved in this audit, so no digest value is asserted.
- These status observations were obtained via GitHub's commit workflow-run and workflow-job endpoints; do not confuse the passing job with a new physical implementation result.

## Scientific interpretation

This closes the previous manually transcribed execution reproducibility gap: the hosted job executed the checked-out committed checker. It is a periodic finite-FIFO conservation negative control, not an independent measurement of real GPU performance. The previously prospective finite-buffer oracle comparison failed the 1.02x materiality gate, and compact greedy's routed area dominance and electrical violations remain binding. **Do not promote the protected oracle to RTL/physical implementation.**

No new RTL simulation, synthesis, legal route, SRAM macro integration, power calibration, matched workload throughput or GPU IPC is established by this run. V296/V317 remain the present lineage; V287 remains historical. Preserve exactly one active mechanism and the current draft PR. Next work must test a realizable stateful scheduler against compact greedy with prospective unseen finite-buffer workloads and explicit area/timing/control overhead, rather than expanding a zero-cost oracle.

## Independent audit caveat

The GitHub workflow success confirms the committed checker completed, not that the checker is exhaustive over all workload distributions or physically realistic. Raw step logs and the printed digest should be separately archived for stronger provenance.
