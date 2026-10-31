# V309: full authenticated Tesla V100 SASS workload profile (2026-10-30)

**Evidence tier:** dynamic NVBit/Accel-Sim SASS instruction rows from an authentic 2020 Tesla V100 Rodinia 2.0-ft archive. **Not** measured GPU cycles, register-bank conflicts, occupancy, power, timing, or RTX 5090 performance.

## Reproduction and independent verification

- Source: [Purdue Tesla V100 Rodinia 2.0-ft archive](https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz).
- Pinned SHA-256: `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1` (21,011,152 compressed bytes).
- Protocol frozen in `V100_DYNAMIC_PROFILE_PROTOCOL_20261030.md` **after bounded prefixes were opened, but before full-corpus decoding**. Therefore these are exploratory workloads, not unseen architecture holdouts.
- [Hosted full-corpus job #40948282729](https://github.com/sushxnthd/vektor/actions/runs/40948282729) **passed**: 4 parser mutants, 6 independent audit mutants, full archive decode, independent conservation audit and 1%-unsupported fail-closed gate.
- [Raw JSON evidence artifact](https://github.com/sushxnthd/vektor/actions/runs/40948282729/artifacts/12929798452) includes application-level and global counts plus independent audit result.

## Authenticated dynamic instruction descriptors

| Descriptor | Observed |
|---|---:|
| Trace files | **210** |
| Distinct Rodinia applications | **11** |
| Parsed active warp-instruction rows | **3,937,565** |
| Zero-active-mask rows (excluded from demand) | 301,313 |
| Unsupported instruction-like rows | **0** |
| Active memory-operation rows (mem_width > 0) | 484,259 (12.30%) |
| Source-register occurrences (including R255) | 5,745,406 |
| Within-instruction unique source registers | 5,261,928 |
| Duplicate source occurrences | 483,478 (8.415% of occurrences) |
| R255 source occurrences | 1,335,308 |
| Active rows with at least two distinct sources | 1,992,954 |

**Free-broadcast strongest control:** the 483,478 duplicate occurrences are an opportunity only against a naive per-occurrence model. A free intra-instruction duplicate-source broadcast baseline already captures them. They do not establish a novel speedup.

## Conditional modulo-bank sensitivity (not physical bank conflicts)

Under a hypothetical bank map `bank(R)=R mod B`, counting active warp-instruction rows whose distinct sources collide **after excluding R255**:

| Hypothetical banks | Collision-bearing rows | Share of rows with >=2 distinct sources |
|---|---:|---:|
| B=2 | 529,327 | 26.56% |
| B=4 | 44,695 | 2.24% |
| B=8 | 15,693 | 0.787% |

R255 is retained in the raw source counts and excluded only in this explicit sensitivity calculation. Its physical semantics and the actual V100 bank mapping were not independently verified. These rates **must not** be interpreted as observed hardware RF stalls. Modulo mapping, bypass behavior, collector ports and warp scheduling are unknown.

## Family heterogeneity (hypothetical B=2, excluding R255)

| Rodinia application | Active rows | Memory-op share | Collision-bearing share of multi-source rows |
|---|---:|---:|---:|
| Hotspot | 1,219,773 | 8.7% | 31.9% |
| LUD | 30,528 | 31.2% | 40.6% |
| Needleman-Wunsch | 51,816 | 27.8% | 49.6% |
| KMeans | 259,113 | 0.4% | 14.3% |
| Streamcluster | 683,288 | 24.9% | 19.3% |

The family differences are real *trace descriptors* but not validated bank-stall differences. Any architectural prediction would require independently matched profiling counters, an actual bank map and same-resource controls. Selecting the apparent highest-conflict family as a winning holdout **after seeing this table** would be post-hoc and is prohibited.

## Independent audit and decision

The independent checker does not import the decoder. It verifies source conservation, active/zero-mask row accounting, per-application/global sums, opcode bounds, nested modulo-bank collision monotonicity and six intentionally corrupted reports. It returned `independent_audit: PASS` with 210 files and 3,937,565 active rows.

**Decision:** V309 successfully replaces synthetic-only evidence with an authenticated 11-application dynamic SASS dataset, but **does not promote a hardware mechanism**. The next physicality gate is to calibrate resource pressure with matched V100 counters or simulator measurements and a realistic RF/collector organization, then freeze a genuinely separate predicted-win and predicted-no-win workload. No RTX 5090 equivalence is claimed.
