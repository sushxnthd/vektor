# Vektor-112: trace-identity discrimination and LSU issue probe

Date: 2026-10-11. Classification: DISCRIMINATION + CAPABILITY-BUILDING.

**Measured (host synthetic SC only):** 1,951 Python/C++ decisions agreed (1,152 discovery, 576 holdout, 216 minimally guided probes, 7 directed). Treating Vortex lane-local `tid` as V111's globally unique thread ID caused 87, 48, 25 and 3 over-rejections respectively against a composite identity model. This falsifies the naive trace-ingestion assumption, not V111's abstract validator when supplied its documented globally unique IDs. No GPU speedup or PPA result.

Pinned public Vortex source: `7fe19369587c087f902c3e2bc2add612aa910a95` (2026-10-07). Source has `trace->cid, wid, cta_id, uuid, PC`; LSU lane entries carry `tid, addr, size`. Source `make_hart_id` combines `(cid,wid,tid)`. Issue address is virtual; optional MMU translates later. CTA lifetime reuse and physical allocation scope are not established.

The complete preregistered Python/C++ experiments, records, checksums and negative controls are in the Vektor-112 reproducibility archive. This branch includes a conservative composite-identity adapter, strict issue-trace parser and source-pinned optional probe. `patch_vortex.py` checks commit and anchors before changing any upstream source. Set `VEKTOR_LSU_TRACE` only after building patched Vortex. **Upstream simulator build and execution are unverified.**

**World model:** KNOWN source fields and host-model agreement; BELIEVED composite logical thread key; CONFLICTING V111 numeric tid vs raw Vortex lane index; FALSIFIED direct substitution of lane tid and inference of DRAM traffic from issue VA; ANOMALOUS frequent collision cases; UNTESTED CTA lifetime, VM translation, real simulator traces, all GPU performance gates.

**Single next action:** compile patched Vortex SimX on a free CI runner, execute a tiny mixed-CTA memory kernel and check record conservation and source/CTA identity against simulator counters. Do not optimize scheduling based on issue-only virtual addresses.

RTX 5090-class: compute, tensor, memory, raster/texture, ray, PPA and software all INCONCLUSIVE. No claim of equivalence. Spend: $0.
