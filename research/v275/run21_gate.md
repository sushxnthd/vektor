# V275 run21 first hardware gate (2026-10-22)

GitHub Actions run 39710577699 (commit 5da701ad95fdd899930c42ae6c1d174b3aee7fda): **success**. Hosted Ubuntu runner installed Icarus Verilog 12.0 and Yosys 0.33. Self-checking directed testbench printed `PASS V275 directed and 100 random-like admission checks`. Generic Yosys synthesis completed successfully. Full generic synthesis log uploaded as Actions artifact ID 12396902166.

URL: https://github.com/sushxnthd/vektor/actions/runs/39710577699

This proves only the tested RTL cases and generic synthesis. The testbench does not cover all interleavings, ASID/mode translation semantics, multiple simultaneous walk completions or system-level throughput. No characterized library mapping, STA, max-cap/slew, wire sensitivity or power result exists. The E1 training sweep is software only. Frozen holdouts remain unopened.

Next discriminator: match two-set indexed, four-way fully associative and prefix-gated associative implementations under Nangate45 cell mapping; require clean electrical checks and area/timing evidence. At most one further plumbing attempt; otherwise retire V275 and pivot. The attempted mapped-synthesis workflow modification was blocked by connector safety checks and was **not** published. No integrated tile change, no novelty or RTX 5090 equivalence claim.
