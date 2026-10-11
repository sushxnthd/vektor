# Vektor-109 world model

**KNOWN:** V108 order-only validator accepts duplicate atomic and mixed-PC cohorts; V109 Python/C++ checkers agree on 2,564 synthetic cases; Vortex trace_csv.py lacks lane effective addresses.

**BELIEVED:** fail-closed cohort checking prevents false legality claims in later online-scheduler experiments.

**CONFLICTING:** V108 checker was used as a legality certificate but only checked dependencies/epochs; its tested generated schedules were well formed.

**FALSIFIED:** dependency ordering alone proves full Wave32 schedule validity.

**ANOMALOUS:** duplicate atomic execution can change final memory without invalidating order-only check.

**UNTESTED:** real SimX lane-address traces; online cohort scheduler; RTL formal proof; register migration, cache timing, occupancy; full GPU throughput/PPA/software gates.

**FOOTHOLD:** reproducible validation-harness counterexample, not GPU performance.

**NEXT:** instrument pinned Vortex SimX LSU for per-lane effective addresses, UUIDs and memory-order/barrier metadata.
