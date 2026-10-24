# V296 seed-replication tool incompatibility (2026-10-25)

The frozen two-seed placement-perturbation experiment in `CTS45_SEED_REPLICATION_PREREG_20261025.md` **did not produce physical measurements**. Both seed 17 and seed 43 failed before global placement in the pinned OpenROAD v2.0-17598-ga008522d8 binary:

```
V296_PLACE_SEED 17
[ERROR STA-0562] global_placement -random_seed is not a known keyword or flag.
```

The same error occurred for seed 43. The generator and independent adversarial self-tests passed, synthesis completed, but no seeded placement/CTS/routing/extraction occurred. The independent aggregate failed closed with `INCOMPLETE_NO_REPLICATION_CLAIM`. This is a **tool-version compatibility failure**, not a negative physical result and not a successful replication.

Original failed experiment: https://github.com/sushxnthd/vektor/actions/runs/40134816281 . Preserved original artifact archives: seed17 ID `12576512137`, seed43 ID `12576048164`, aggregate ID `12575998216`. Both original contestant logs were independently inspected from their archived ZIPs. The frozen seed protocol will not be silently rewritten to use different randomization semantics.

A distinct physical intervention may be preregistered to vary I/O geometry under the pinned binary. Such an experiment would test **pin/wire sensitivity**, not independent placement-seed replication. V296 controller-level Pareto evidence from the original setup250 and 10 fF runs is unaffected, but seed robustness remains untested. No GPU tile/frequency/power/workload claim follows.
