# Executed joint-mask checker reproduction (2026-11-05 UTC)

Evidence tier: **synthetic exact arithmetic**, not RTL, physical signoff, or GPU throughput.

The source at `research/v317/audit_joint_mask_law_exhaustive.py` was read from the canonical research branch. Its complete logic was reproduced in a local Python 3 execution environment, using `fractions.Fraction`, `itertools.combinations`, and the same assertions. Output:

```text
PASS: 495 exact joint tables, service range 1..2
```

The nine mask-pair probabilities were enumerated on a denominator-four grid; every configuration satisfied the joint-mask service identity, correlation correction, and marginal bounds. This closes the earlier **unexecuted checker** evidence gap only for this synthetic audit. The fetched GitHub file was not executed byte-for-byte, and no hosted CI result is claimed.

**Hard stop on physical interpretation:** the 2026-11-02 matched routed comparison still has compact-greedy area 21,314.6 µm² and pairwise area 21,324.7 µm², with 20 and 21 electrical violations respectively. The pairwise area thesis is falsified against compact greedy; the synthetic law does not rehabilitate it. No additional scheduling-only synthetic exercise should be interpreted as a replacement for electrically legal matched RTL and real-kernel results. No positive V317 tile-throughput claim is supported.
