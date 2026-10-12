# Vektor-126 preregistration — 2026-10-12

Class: DISCRIMINATION + CAPABILITY-BUILDING. Branch: research/kpx-wave32-reset-contract-126. Parent: V125 Wave32 RTL candidate.

## Claims under test
P1: V125 commit_o can be high during synchronous reset if valid_i=1 and opcode is legal, despite no architectural state update. Corrected interface must assert neither commit nor fault while reset is active.
P2: An explicitly balanced 32-lane modulo-2^32 reduction tree computes exactly the same bit pattern as the original serial masked accumulator for every 32-bit input/mask, including overflow.
P3: The longest chain of 32-bit additions in a 32-leaf balanced tree is 5 versus 31 for the serial loop. This is structural depth, **not** measured timing or PPA.

## Fixed experiments
1. Evaluate reset/valid/opcode truth tables from source and a separate handshake contract.
2. Execute 1,000,000 deterministic C++ reduction vectors (seed 1262026), 12.5% minimally guided mask/operand probes, comparing serial and balanced trees to a separate Python oracle on a smaller independent sample.
3. Prepare HDL testbench for reset collision, invalid opcodes, stack overflow, and arithmetic equivalence; execute Icarus and Yosys only where tools are actually available.
4. Preserve all failures and mark RTL/STA gates inconclusive until actual HDL simulation/synthesis.

## Adversarial tests
Explorer: tree reducer; Skeptic: reduction tree changes synthesis resource mapping and may increase wire cost; Experimentalist: reset/valid overlap and overflow; Analyst: structural depth != MHz; Anomaly Hunter: group mismatches by mask popcount and overflow; Prior-Art Auditor: balanced adder trees and reset gating are established, not novel; Replicator: C++ and Python independently; Theorist: modular addition associativity implies bitwise equivalence.
