# V206 ARCHITECTURE ledger

- **Integrated tile:** No RTL integration. V151/V146 conservative FP32/operand collector references remain unchanged.
- **Hard correctness condition:** WB wave ID, architectural/physical register ID and producer version must all match each requested operand; equal wave and register alone are insufficient. RF responses also require upstream version/wave qualification, which the standalone V206 module does not enforce.
- **Hardware cost:** Version-qualified bypass adds equality comparators and enqueue-data selection, but mapped area, timing, wire-load, slew, max-cap and energy remain unknown. Do not count synthetic IPC as a Pareto improvement.
- **Physicality:** STOP. V205/V206 cannot graduate to Vektor tile without functional RTL simulation, matched synthesis, electrical checks and timing.
- **Build continuation:** Existing V-Tile scheduling/RF arbitration and FP32 slice remain independent build priorities. The next active research kernel must have a demonstrable effect on issue/traffic/throughput and a credible physical evaluation route.
- **Evidence class:** exhaustive Boolean key-matching model + unexecuted version-qualified RTL source in local package; not physically qualified.
- **Prior art:** Ordinary operand bypass and forwarding are established. No new architectural law claimed.
