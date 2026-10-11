# Vektor-113 prospective holdout registration

This was recorded after the initial 330-case development/holdout/surprise run, **before** running 64 additional prospective cases. Do not relabel the first 330 cases as preregistered.

**Classification:** DISCRIMINATION and CAPABILITY-BUILDING. **Mechanism:** Vortex CTA slot reuse makes (cid,cta_id) non-unique across CTA lifetimes. **Prediction:** Python/C++ restricted oracles agree on every prospective case; at least one distinct-generation shared-memory false hazard is eliminated; at least one global-memory hazard is preserved; all deliberately malformed CTA lifecycles fail closed.

**Prospective seeds:** 120000 through 120063 inclusive. Equal-budget controls include same-generation and global-memory overlaps, and malformed-lifecycle negatives. The 42 minimally guided probes represent 10.7% of all 394 cases. Exact counts were not preregistered.

**Outcome:** 394/394 independent matches across all groups; 33 legacy false shared hazards; 25 preserved global hazards; 279 malformed traces rejected. The prospective qualitative predictions held. These are synthetic host traces, not Vortex execution or GPU performance.

**Residual:** zero against the binary predictions; no preregistered numerical count to compare. **Competing explanation:** V112 had already marked the CTA identity mapping unverified. **Uncertainty:** patch not compiled/executed, possible logging omissions, issue versus retirement ordering. **Cheapest next experiment:** source-pinned SimX multi-CTA run with balanced lifecycle and LSU issue record conservation.
