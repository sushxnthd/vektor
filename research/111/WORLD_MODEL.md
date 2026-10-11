# Vektor-111 world model, 2026-10-11

KNOWN: Python/C++ abstract validators matched 1955/1955 cases; V110 over-rejected 91 random schedules relative to scoped model.
BELIEVED: explicit address-space metadata may reduce conservative scheduler restrictions without compromising the abstract SC reference order.
CONFLICTING: device-wide SC global-memory ordering is conservative and may over-restrict real GPU memory models.
FALSIFIED: equal numerical addresses necessarily alias across shared/local instances; V110 signature always prevents mixed-CTA wave formation.
ANOMALOUS: V110 accepted a directed same-PC mixed-CTA wave; near-2^64 surprise generator required a legal-address repair.
UNTESTED: actual Vortex LSU address-space mapping, real GPU memory model, RTL simulation/synthesis/PPA, performance effects.

Closed branches retained: V105 future-address oracle, V107 coalescer-count-to-DRAM extrapolation, V108 permissive legality, V109 starting-address dependence, V110 unscoped address identity.
Next decisive action: obtain Vortex SimX LSU per-lane trace with space, CTA, thread, address, width, and synchronization.
