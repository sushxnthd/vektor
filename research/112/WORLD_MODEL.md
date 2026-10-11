# Vektor-112 evolving world model
KNOWN: Vortex source at 7fe19369587c087f902c3e2bc2add612aa910a95 has cid/wid/cta_id/uuid/PC and LSU lane-local tid/VA/size; local Python/C++ restricted SC checks matched 1951/1951.
BELIEVED: Composite logical thread identity is a safer trace-ingestion key than numeric lane tid.
CONFLICTING: V111 assumes globally unique tid, whereas Vortex raw LSU tid is lane-local; per-CTA shared-memory physical namespace still needs confirmation.
FALSIFIED: Direct substitution of raw Vortex tid into V111 and interpretation of LSU issue VA as DRAM/physical evidence.
ANOMALOUS: High collision-driven over-rejection rate in synthetic probes; Vortex source notes simulator/RTL shared-AMO discrepancy.
UNTESTED: Patched Vortex compilation/execution, CTA lifetime reuse, physical aliasing, real cache/NoC traffic, all full-GPU capability gates.
Cheapest next discriminating experiment: compile patched Vortex and capture a mixed-CTA kernel with actual issue records; cross-check counts and identities.
