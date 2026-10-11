# Vektor-113: CTA slot lifetime and trace integrity

**Source-backed correction.** In public Vortex at `7fe19369587c087f902c3e2bc2add612aa910a95`, `sim/simx/cta_dispatcher.cpp` assigns `out->cta_id=cur_slot_`, and releases that slot after its final warp completes. Thus `(cid,cta_id)` is not lifetime-unique. V112 explicitly marked this assumption unverified; V113 resolves it at the source level.

**Implementation in this branch:** `lifetime.py` is a fail-closed lifecycle/LSU issue parser with CTA generation tagging and directed byte-hazard tests. `source_audit.py` checks pinned upstream source. `probe.h` is an opt-in formatter with allocation/release and issue-stage event types. CI compiles the probe in isolation and checks source anchors; it does **not** compile or execute the instrumented Vortex simulator. The dual-site patch, independent C++ replica, raw experiment data and SHA256 manifest are in the separate complete V113 reproducibility package.

**Synthetic host experiment:** 192 development, 96 holdout, 42 minimally guided probes, and 64 prospectively registered cases (394 total). Python/C++ restricted oracles agreed on **394/394**; 33 cases showed spurious shared-memory hazards with slot-only identity; 25 preserved global-memory hazards across generations; 279 malformed traces were rejected. This is not a GPU speedup or measured hardware result.

**Run:** `python research/113/lifetime.py`. See `PREREGISTRATION.md` and `WORLD_MODEL.md`. V112's existing LSU probe is issue-stage only. Never infer physical addresses, DRAM traffic, completion order or GPU equivalence from these host models.

**Single next decisive action:** compile and run a source-pinned dual-site instrumented Vortex SimX multi-CTA workload; independently verify balanced CTA lifetimes and issue-event conservation before scheduling experiments.

**RTX 5090-class gate:** all compute, tensor, memory, graphics, ray, frequency, area, power and software gates remain INCONCLUSIVE. Personal expenditure $0.
