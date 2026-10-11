# Discovery Protocol V2 — Vektor-113

- **KNOWN:** Vortex pinned `cta_dispatcher.cpp` assigns `out->cta_id=cur_slot_`, tracks slot warp count, frees slot at final warp completion. V113 Python/C++ restricted synthetic oracle agrees 394/394. V112's LSU probe records issue-stage virtual addresses only.
- **BELIEVED:** Lifecycle generation is necessary for reliable shared-memory identity when ingesting traces across CTA slot reuse.
- **CONFLICTING:** V112's provisional `(cid,cta_id)` allocation key versus source-proven slot reuse.
- **FALSIFIED:** A reusable `(cid,slot)` pair is a lifetime-unique CTA identity. The false-hazard control reproduced 33 cases.
- **ANOMALOUS:** Identity aliasing reappears at a different level after fixing lane-local thread IDs; cluster with prior identity/conservation bugs as a first-class trace-integrity bottleneck.
- **UNTESTED:** Full patched Vortex build/run, true CTA begin/end event balance in simulator, issue-event completeness, address translation, cache traffic, real memory ordering, RTX 5090-class gate.
- **Experiment classification:** DISCRIMINATION + CAPABILITY-BUILDING. Mechanism: slot reuse. Prediction: new epochs eliminate false shared-memory alias while preserving global hazards. Outcome: 33 false hazards removed, 25 global hazards preserved; qualitative predictions met. Residual: exact counts not preregistered. Competing explanation: V112 already marked key unverified. Uncertainty: source patch unbuilt, host synthetic only.
- **Next cheapest discrimination:** pinned SimX compile and mixed-CTA trace run, compare independent counters, no speedup claim.
- **Prior art:** CTA generations/epochs and trace-lifetime tagging are standard; no novelty claim.
- **Adversarial review:** Explorer epoch-aware keys; Skeptic missing records/observer order; Experimentalist slot-reuse control; Analyst host-only; Anomaly Hunter recurrent identity alias; Prior-Art Auditor standard technique; Replicator C++; Theorist allocation identity must include lifetime.
