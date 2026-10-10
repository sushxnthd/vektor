# Vektor-085: coherent RF bank accounting, conditional WB reservation and RTL optimization

**2026-10-10.** The V-Tile study combines SIMULATED integer-valued instruction-token pipeline experiments with a narrow FORMALLY VERIFIED and generically SYNTHESIZED combinational RF grant arbiter. **No RTX 5090-class claim.**

## Software-model findings

For 8 waves ×128 instructions, spread-bank trace, latency 3, cache off: unreserved shared3 = 490 simulated cycles; split2-read+1-write = 401; shared3 with read cap2 = 401; shared3 with issue-time future writeback reservation = **395**; split+reservation = 397. Selected 490→395 improvement is **19.4%** in synthetic model, not GPU throughput. In 96 unseen cases, reservation improved 47, worsened 17, tied 32; worst regression +113 cycles. **No universal adoption.** A four-cycle forecast throttle failed generalization (17 wins,31 losses,48 ties).

The single-bank 2-source/1-destination no-cache resource bound is shared p ports <= p/3 instruction tokens/cycle; at 1,024 tokens shared2 achieved 0.6654, split1+1 0.4988, split2+1 0.9942. All synthetic runs checked against a sequential interpreter and Python trace auditor; 75 Python tests passed. Independent C++17 replay verified 2,560 commits across three fixed traces, but is **not** an independent cycle-level simulator.

The full executable simulation/data package `vektor_085_shared_rf_writeback.zip` (SHA-256 `8991fbe156316e4fe8199edc5d411da632a2c9804d77be9c14fae5b647cbeb8f`) is attached to the research run. It is **not yet committed** to this branch. This branch preserves compact preregistration, world model, target ledger, and experimental RTL.

## Narrow RTL milestone

Preregistered bank-major static-index optimization reduced Yosys generic gate cells **18,752→2,036 (89.1425%)** under identical generic synthesis flows. 10,000 randomized Icarus Verilog equivalence vectors passed. Yosys formally proved **76/76** default-parameter combinational equivalence cells, none unproven. See [evidence and run links](RTL_FORMAL_RESULT.md).

This is a coding/synthesis implementation improvement, **not** ASIC area, timing, power, frequency, fairness, or proof of the proposed sequential writeback reservation mechanism.

## Next decisive action

Integrate coherent RAW/WAW and finite read/write accounting into canonical `sim/vektor/pipeline.py`; prove per-bank grant safety and parameterized equivalence; implement a sequential reservation table and run process-qualified physical estimates when feasible. GPGPU-Sim documents the established operand collector/scoreboard prior art: https://gpgpu-sim.org/manual/index.php/Main_Page . **All RTX 5090-class capability gates: INCONCLUSIVE.**
