# Vektor-086: sequential fixed-latency writeback reservation

Date: 2026-10-10. Parent: `research/rf-writeback-085` @ `2893251dbbe416f81a69bf5306c16c9ee8bc07df`.

This milestone adds a synthesizable bank-major future-writeback reservation controller and an independent absolute-cycle event-calendar oracle. **It is not a complete register file or GPU pipeline.** It has no values, register IDs, version tags, cancellation, variable-latency completion, forwarding or replay.

## Verified results

GitHub Actions [run 38055424976](https://github.com/sushxnthd/vektor/actions/runs/38055424976), source commit `5cc1b0dfd1b95614d1a2c584e146d04e176bb42a`:
- Default 4 banks, 4 requests, 1 write port/bank, latency 1..4: **4,096/4,096 cycles** match the independent oracle for grants and due counts.
- Alternate 3 banks, 6 requests, 2 write ports/bank, latency 1..5: **2,048/2,048 cycles** match.
- Deterministic seeds 20261010 and 20261011. **12.5%** of cycles in each trace are minimally guided random probes.
- Yosys 0.33 generic synthesis: **694 generic cells**, including **16 flip-flops** at default parameters. This is not mapped ASIC area, clock speed, power, or timing.
- Existing simulator and RTL workflows also ran on the research branch. No main-branch changes.

- Bounded Yosys SAT safety proof: [run 38055585967](https://github.com/sushxnthd/vektor/actions/runs/38055585967) proves slot counts <= bank write ports for ten steps from a zero-initialized state. **Not** an unbounded or liveness proof. Current branch head includes the formal assertions behind `FORMAL`.

## Reproduce without paid resources

```sh
mkdir -p build/086
python3 experiments/reservation_reference_086.py build/086/p1.vec
python3 experiments/reservation_reference_086.py build/086/p2.vec --banks 3 --reqs 6 --max-latency 5 --ports 2 --cycles 2048 --seed 20261011
iverilog -g2012 -s tb_rf_wb_reservation_086 -o build/086/tb1 rtl/vtile/rf_wb_reservation_086.sv verification/rtl/tb_rf_wb_reservation_086.sv
vvp build/086/tb1 +VEC=build/086/p1.vec
iverilog -g2012 -s tb_rf_wb_reservation_086 -Ptb_rf_wb_reservation_086.BANKS=3 -Ptb_rf_wb_reservation_086.REQS=6 -Ptb_rf_wb_reservation_086.MAX_LATENCY=5 -Ptb_rf_wb_reservation_086.WB_PORTS_PER_BANK=2 -Ptb_rf_wb_reservation_086.CYCLES=2048 -o build/086/tb2 rtl/vtile/rf_wb_reservation_086.sv verification/rtl/tb_rf_wb_reservation_086.sv
vvp build/086/tb2 +VEC=build/086/p2.vec
yosys -p 'read_verilog -sv rtl/vtile/rf_wb_reservation_086.sv; synth -top rf_wb_reservation_086; stat'
yosys -p 'read_verilog -formal -sv -D FORMAL rtl/vtile/rf_wb_reservation_086.sv; prep -top rf_wb_reservation_086; async2sync; dffunmap; sat -seq 10 -set-init-zero -prove-asserts -verify'
```

## Design constraints

A request with latency L reserves one write port for the bank at cycle now+L. Slot 0 counts writes due now. The last slot is a zero sentinel, permitting L=MAX_LATENCY. Asynchronous active-low reset flushes reservations. Out-of-range bank or latency is rejected. A grant does **not** mean that a value was computed, stored or architecturally committed.

The fixed-priority policy can indefinitely starve clients 1..3 under four continuous same-bank same-latency requests: the independent reference admits [1000,0,0,0] over 1000 cycles. This is a **negative result and design blocker**, not a claim of fairness. Correctness of variable-latency execution, WAW/RAW hazards and integration into V-Tile remain untested.

## Next decisive experiment

Build a fair, cancellable writeback reservation protocol with age/generation tags, test against an independent completion-event oracle, and compare equal-budget area/throughput with fixed priority. Then integrate with the coherent V-Tile simulator.

Prior-art audit: bank arbitration and future resource reservations are established computer-architecture mechanisms; no novelty claimed. RTX 5090-class performance, software, power, frequency and area gates remain **INCONCLUSIVE**. Personal spend $0.
