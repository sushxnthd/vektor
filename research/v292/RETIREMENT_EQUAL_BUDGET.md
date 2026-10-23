# V292 equal-resource retirement gate — 2026-10-23

**Decision: RETIRE V292. Evidence E0 (functional/equal-resource model), not an electrical falsification.**

The V292 RTL exposes a single 1024-bit lane-indexed data bus, two 32-bit masks, two 16-bit tags and two collector credits. Its entire decision is: accept packet A if one credit exists; additionally accept B if two credits exist and `(mask_a & mask_b)==0`. Data from disjoint lanes are multiplexed into the same 1024-bit beat.

The strongest *same-resource conventional sector packer* can make precisely that admission decision with the **same** two pending packets, two credits, masks, tags, per-lane selector and output bus. This is not a new architecture mechanism against that control. The lower-bound serial-only comparison is invalid as evidence of a breakthrough.

An independent reference implementation compared two algorithms for 65,536 exhaustive 8-bit mask intersections embedded in 32 lanes, and 200,000 randomized 32-lane mask pairs, for **265,536 configurations and zero mismatches**. Raw modeled results (40,000 per regime):

| Frozen regime | Packets/beat, V292 and matched packer | V292/control |
|---|---:|---:|
| sparse q=.08, two credits | 1.81470 | 1.0000 |
| dense q=.70, two credits | 1.00000 | 1.0000 |
| sparse q=.08, one credit | 1.00000 | 1.0000 |
| training q=.20, two credits | 1.27220 | 1.0000 |
| training q=.50, two credits | 1.00015 | 1.0000 |

The frozen sparse-versus-dense *serial-only* directional prediction holds, but the gain is fully reproduced by the matched control. It therefore **fails the preregistered equal-budget kill criterion** (advantage <= 1%). No need to spend additional runs optimizing an isolated 1,024-mux block.

**Independent caveats:** This result does not prove post-synthesis area, electrical max-cap/slew, STA, power or integrated V-Tile performance. The repository contains no verified lane-addressable L1-to-collector return subsystem or two-destination collector contract; do not treat the overlay as physically integrated. Earlier generic synthesis reported 2,247 cells, including 1,024 muxes, but that is not characterized area.

**Architecture consequence:** V-Tile unchanged; no memory-throughput, FP32, or RTX 5090 equivalence claim. V287 remains retired.

**Reproduction:** `python3 research/v292/equal_budget_oracle.py` prints the seeded raw result JSON. Next active kernel must deliberately search a positive boundary law, rather than revisiting packet overlay under a different name.
