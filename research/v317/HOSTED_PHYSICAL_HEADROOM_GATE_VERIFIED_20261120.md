# Hosted independent physical-headroom gate: verification (2026-11-20 UTC)

Evidence tier: hosted execution of a necessary mathematical screening bound, **not** physical signoff or measured GPU throughput.

- Existing research branch: `research/v317-sass-provenance-gate`; existing draft PR #34.
- Source commit tested: `98371d54113a5f5dc3edb6e2560ff540f22cb5b1`.
- Hosted GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/44789624555 (success).
- Job `independent-periodic-audit` (136473518030), completed successfully.
- Step 14, `Independent necessary physical-headroom falsification (development only)`: success.
- Step 15, `Digest independent physical-headroom source`: success.
- Development replay, seed-cluster sensitivity, structural audit, finite-FIFO regression and conservation checker steps also succeeded.
- Checker: `research/v317/rtl/independent_physical_headroom_gate_20261120.py`, fetched blob SHA `2558f1133a420c01dac2ce53823ae9b9e81bb679`.

## Interpretation and limitations

The implemented policy is alternating middle-slot priority, not general four-way rotating priority. Its frozen development geometric-mean throughput ratio is 0.999935x versus equal-resource compact greedy. The necessary optimistic throughput bound is `min(service_ratio * clock_ratio * occupancy_ratio, bandwidth_ratio)`; the strongest observed development seed is 1.000058828344x before physical overhead, below the preregistered 1.02x relevance threshold. This bound is a screening model with multiplicative factors, **not** a calibrated end-to-end GPU performance prediction. No holdout seeds were opened. No new RTL synthesis, electrically legal routing, integrated SRAM, power measurement, or GPU IPC is established. The prior compact-baseline routed area/electrical failures remain binding. The policy remains NO-GO; no new mechanism activated.

Do not infer RTX 5090 equivalence. Next substantive architectural candidate requires independent prior-art screen, frozen equal-resource control, demonstrable finite-buffer service headroom, and only then physical escalation. Preserve V296/V317 lineage and historical V287 status.
