# SCIENCE V174

Question: Does the V153 cutset retain timing and area-delay advantages over V151 as input arrival varies?

V156 baseline: 12.93 ns control (register-launched), 8.35 ns cutset (input-launched). Mapped area: 7558.39 versus 7821.46 units.

Mechanism: With a fixed netlist and a uniform input-delay shift delta, input-launched path delays rise by delta, while other path delays remain fixed. Thus cutset delay is 8.35+delta, while control delay lies in [12.93,12.93+delta]. This is an exact conditional bound, not a new OpenSTA measurement.

Predictions: Guaranteed >=10% timing advantage until input delay 3.337 ns, area-delay advantage until 4.195107 ns, raw timing advantage until 4.63 ns. These are guarantee horizons, not observed crossover points.

Falsification: matched seven-point OpenSTA sweep, then physical PPA and unseen FP32 workloads. Publishability and architecture gates remain unmet.

Kill: after three uninformative substantive runs, pivot the kernel; retain automation and negative evidence.
