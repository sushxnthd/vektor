# Vektor-070 independent checks and RTL evidence

Commit under test: 4b77446665ab217ffefa21c90d5a7d5fd0e2b187.
GitHub Actions: https://github.com/sushxnthd/vektor/actions/runs/37998123580

- Structured synthetic event model: 96 runs + 12 minimally guided probes. Strong: 18,197 retirements, 0 stale-origin credits. Early: 17 false DATA + 15 false ACK credits across 8 runs.
- Unseen holdout: 36 strong-fence runs, 5,236 retirements, 0 stale-origin credits. Early: 7/24 unsafe, 255 false DATA + 115 false ACK credits. All preregistered predictions passed.
- Icarus Verilog receiver directed simulation: PASS.
- Icarus Verilog sender/receiver integrated ACK-loss/retry/fence simulation: PASS (4 DATA sends, 2 logical deliveries).
- Yosys generic synthesis of receiver: PASS, 41 generic cells (default UID_W=4). **Not technology area, timing, or power.**
- Independent C++ small-state alias enumeration: 19 bounded traces, 18 early-unsafe, 2 ACK-only-unsafe, 2 DATA-only-unsafe, 0 strong-fence-unsafe among one admitted zero-old-copy trace. This verifies a logical boundary, not numerical replication of the event simulator.

Limitations: trusted external physical quiescence; single active transaction; ideal zero-latency RTL integration; no formal end-to-end router proof; no synthesized clock or physical PPA; no GPU-level performance inference.
