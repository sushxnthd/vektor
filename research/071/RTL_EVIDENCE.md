# Vektor-071 RTL verification evidence

Date: 2026-10-10. Passing CI run at commit 2e97bdf:
https://github.com/sushxnthd/vektor/actions/runs/37999812399

- Independent Python deque-vs-ring: PASS, 1,200 paired traces, 240,000 cycle transitions.
- Icarus Verilog bounded-router directed test: PASS.
- Icarus Verilog sender/router/receiver integration: PASS, two sequential same-UID transactions, four DATA admissions, twelve ACK deliveries (clones/retries).
- Yosys generic synthesis: PASS, 300 generic cells, UID_W=4, DEPTH=4.
- Yosys warning: DATA and ACK memories replaced with registers, not SRAM inference or physical feasibility evidence.
- Initial CI failed because testbench read quiescent in the same delta cycle as changing external_inflight. A settling delay corrected the testbench; RTL was unchanged.

Not exhaustive formal proof. No routed area, timing, power, silicon, cross-reset, out-of-band replay, or multi-hop NoC verification.
