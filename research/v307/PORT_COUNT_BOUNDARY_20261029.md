# V307 physical port-count boundary (analytical, 2026-10-29)

The pilot's eight-bank assumption is **not** a demonstrated configuration for an RTX 5090 subcore. Barnes, Shen and Rogers, HPCA 2023, report two RF banks per subcore for A100/V100-like partitioned GPU models; modern Blackwell bank topology is not established by that source. The V307 pilot also unrealistically requires both operand reads to complete atomically in the same issue cycle, omitting multi-cycle operand collectors.

For independent, two-distinct-bank operands, the exact compatibility law in `COMPATIBILITY_LAW_PILOT_20261029.md` yields:

| Banks per independent scheduler domain B | P(two mutually disjoint instructions) | P(three mutually disjoint instructions) |
|---|---:|---:|
| 2 | 0% | 0% |
| 4 | 16.6667% | 0% |
| 6 | 40.0000% | 2.6667% |
| 8 (V307 pilot) | 53.5714% | 11.4796% |
| 16 | 75.8333% | 41.7083% |

At **B=2**, every two-source instruction consumes both banks; instantaneous issue capacity is one. All three policies select at most one instruction per cycle, so the modeled multi-issue bank-pressure benefit cannot exist under the pilot's atomic-read assumption. At B=4, three-way simultaneous issue is impossible. This is an exact *model boundary*, not a measurement of actual GPU IPC.

**Mandatory falsifier:** before promoting V307 beyond the synthetic pilot, reproduce a realistic bank/collector configuration (including staged reads, per-subcore partitioning and occupancy) and compare to the strongest same-information scheduler. If gains vanish at realistic bank counts or fail matched timing/area, retire. Do not interpret eight-bank synthetic gains as NVIDIA Blackwell evidence.

Source: https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf

No holdout seeds were opened and no scheduler parameters were changed.
