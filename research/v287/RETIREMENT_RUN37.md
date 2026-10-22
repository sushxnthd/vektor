# V287 run37: RETIRED after matched-interface resource bound

The combinational RTL gate passed 95,536 cases (65,536 mask pairs plus 30,000 randomized configurations), including 6,217 fused cases. See GitHub Actions v287-physicality run 39830168067, job 120003894217.

The first characterized synthesis attempt did **not** complete. Yosys ABC mapped Nangate45 cells, but `check -assert` rejected undriven nets because Liberty cell port directions were not imported as blackboxes for the check. This is a tool-script error, not an electrical failure; mapped area, timing, max-cap, slew and power are **not** claimed.

**Decisive intended-tile control:** Vektor-1A currently specifies 128 FP32 lanes per tile, wave size 32 and four schedulers. The actual `rtl/vtile/issue_control.sv` exports four wave issue slots and the `rf_bank_arbiter.sv` grants at most four wave operand requests per cycle. V287 fusion requires two distinct warp operand sets for each fused issue, so under the same RF grants its theoretical throughput ceiling is `min(8 SIMD warp issue capacity, 4 RF wave grants) = 4`. The strongest equal-resource baseline already has `min(4 SIMD slots, 4 RF grants) = 4`. The equality holds for any smaller RF grant rate. Therefore the original 2x isolated one-SIMD issue prediction cannot be extrapolated to the specified V-Tile. A positive tile-level throughput law requires additional RF/collector bandwidth or fewer SIMD issue slots, neither an equal-resource comparison here.

This is **an architectural interface/bottleneck falsification under explicit saturation assumptions**, not post-layout physical falsification. The isolated 8-lane RTL remains valid for its own scope but cannot support a tile throughput breakthrough. It omits real RF read addressing, storage, collector refill, scoreboard and reconvergence. Retire V287 rather than spend a second CI-only run refining synthesis wrappers.

Evidence: E1 combinational RTL simulation, E0 integrated upper-bound proof; **no clean electrical STA**. FP32 V153/V156 remain electrically disqualified. No RTX 5090-class claim. See `port_budget_falsifier.py` for reproducible bound.
