# V309 source-level falsification: visible SASS mask does not necessarily identify serialized addresses (2026-10-30)

## Source evidence and qualification
The [dated 2020-03-09 upstream tracer snapshot](https://github.com/accel-sim/accel-sim-framework/blob/0e2fddcdef37fc59ad786553892b75567a5f2cdb/util/tracer_nvbit/tracer_tool/tracer_tool.cu#L660-L736) contains the following asymmetry:

- Line 662: the serialized trace mask is `ma->active_mask & ma->predicate_mask`.
- Line 684: the address-compression mask is initialized from `ma->active_mask`, **not** the printed mask.
- Lines 695-729: format-1 base and stride are computed from the unmasked active lanes.
- Lines 731-735: format-0 explicitly writes one address per unmasked active lane.

This source snapshot predates the [2020-03-18 V100 Rodinia archive](https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz), but a date match does not establish that the snapshot generated those files. All conclusions below are **conditional on the snapshot's producer semantics**.

## Exact nonidentifiability counterexample
Let the printed active mask M contain lanes 2 and 3. Let the printed memory encoding be `format1 base=0x101c stride=4 width=4`. Two distinct underlying producer states generate exactly that same visible mask and compressed address payload:

| Hidden original A | Hidden predicate P | Printed M=A&P | Address of lane 2 | Address of lane 3 | 32B sectors |
|---|---|---|---|---|---|
| lanes 0,1,2,3 | lanes 2,3 | lanes 2,3 | 0x1024 | 0x1028 | **1** |
| lanes 2,3 | lanes 2,3 | lanes 2,3 | 0x101c | 0x1020 | **2** |

In both cases A is contiguous and the original lane-address sequence has stride 4, so the 2020 source would emit format 1. The serialized trace rows are observationally identical, yet the actual active-lane 32-byte sector count differs. Therefore **the visible trace alone cannot uniquely determine sector topology** under these producer semantics, even for contiguous printed masks.

The ambiguity is not an implementation bug in the new decoder: it is a loss of information in the serialization mapping. No amount of downstream model sophistication can recover the missing original A/P without extra evidence.

## Sharp source-conditional envelope
For printed M, base b, stride d, width w and aligned sector size g, let `L=setbits(M)`. The first lane s of original contiguous A can range from 0 to min(L), subject to producer constraints. For each s:

`addr_s(l) = b + (l-s)*d` for l in L.

`S_g(s) = | union_{l in L} { floor(x/g) : x in [addr_s(l), addr_s(l)+w) } |`.

The sharp candidate-set bounds are `min_s S_g(s) <= true S_g <= max_s S_g(s)`. These bounds are **sharp within the stated source model**, because every valid s has a contiguous original A and some P yielding M. An interval that collapses to a point identifies the sector count even when absolute addresses remain ambiguous. No unqualified hardware transaction, cache behavior or GPU stall inference follows.

For format 0, let n be the number of serialized addresses. Under this source model, n=popcount(A), while the visible mask M=A&P. If n=popcount(M), then A=M and active addresses can be mapped exactly in lane order. If n>popcount(M), the token-to-visible-lane mapping is generally ambiguous. If n<popcount(M) or n>32, this producer model is contradicted for that row.

## Consequence for the previous report
The prior [memory-sector negative report](V100_MEMORY_SECTOR_TOPOLOGY_NEGATIVE_20261030.md) treated contiguous visible format-1 masks as unambiguously decoded. This assumption is **not justified by the 2020 producer snapshot**. Its 1,096,117 decoded 32-byte sectors and 32.9867% byte utilization are conditional on that earlier address-mapping assumption, not independently verified physical facts. The fixed-address ideal-coalescer lower-bound theorem remains mathematically correct, but the trace-specific inputs to it may be uncertain.

## Reproducibility and decision
- [Frozen source-conditional protocol](LEGACY_PREDICATE_MASK_PROTOCOL_20261030.md).
- [Executable 2,295-case envelope oracle and authenticated full-corpus provenance analyzer](legacy_predicate_mask_provenance.py).
- [Hosted workflow](https://github.com/sushxnthd/vektor/actions/runs/40986243894). Full-corpus outcome must not be claimed until CI completes and is independently inspected.

**Decision:** no new hardware mechanism promoted; previous retired mechanisms remain retired. Before another GPU hardware proposal, establish producer provenance and matched counter/cycle calibration. The existing Rodinia corpus is exploratory, not an unseen holdout. No GPU IPC, power, routed timing, or RTX 5090-equivalence result is claimed.
