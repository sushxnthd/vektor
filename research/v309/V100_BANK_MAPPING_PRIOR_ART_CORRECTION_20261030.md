# V309 prior-art correction: physically grounded V100 bank map (2026-10-30)

**Literature audit completed while the new sensitivity sweep was still running; no new full-corpus result was inspected before this note.** The frozen experiment and decision gates remain unchanged.

## Critical correction

Jia, Maggioni, Staiger and Scarpazza, *Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking*, arXiv:1804.06826 (18 April 2018), section 3.5, report **two 64-bit register-file banks** on Volta and a **register-index modulo-two bank assignment**. Their FFMA microbenchmark detects conflict when all three 32-bit source operands fall in one bank.

Source: https://arxiv.org/abs/1804.06826 ; accessible report section 3.5: https://picture.iczhiku.com/resource/paper/SYkWpgpDWRtpubbn.pdf

Consequences for the ongoing sweep:

1. `mod2` is **not merely an arbitrary hypothetical map for V100**: there is independent microbenchmark evidence for it. `xor2` remains a deliberately counterfactual mapping sensitivity, potentially useful for studying *transfer* to other bank organizations, **not** a competing account of known V100 silicon.
2. A 64-bit bank can potentially service two 32-bit source operands; the published FFMA three-same-bank conflict observation is consistent with the sweep's **P=2** idealized bank-service model. However, bank width alone does not prove an unrestricted two-port read implementation, and the paper's FFMA observation cannot be generalized to all SASS opcodes without validation.
3. Therefore the original P=1 isolated-service model is likely **overly pessimistic for V100 FFMA**, and a large P=1 mod2 score is not evidence of a hardware bottleneck. The physically more relevant screening question is how much P=2 modeled serialization remains, especially on three-source arithmetic instructions.
4. Even a nonzero P=2 score is **not a measured stall**: scheduling, bypasses, operand collectors, per-opcode behavior and latency hiding remain unmodeled.
5. Rank inversions between modulo and XOR maps should be interpreted as **lack of transfer robustness across hypothetical mapping choices**, not as uncertainty about the measured V100 modulo-two mapping.

## Research decision implication

Do not promote bank-remapping or conflict-aware scheduling solely from this trace-derived model. The next physicality gate must reproduce published V100 FFMA bank-conflict behavior in an independent model or microbenchmark, then compare with calibrated counters and matched resources. The existing V309 full-corpus sweep remains a qualification/falsification experiment, not a new mechanism. No RTX 5090 mapping is inferred.
