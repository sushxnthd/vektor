# Vektor-115 preregistration — 2026-10-12

Classification: DISCRIMINATION + CAPABILITY-BUILDING; 48/432 = 11.1% SURPRISE probes.

Hypothesis H115A: joining post-MMU PA records to pre-MMU VA records by (uuid,hart_id,tag) and FIFO order can misattribute translations when those fields repeat and outputs reorder. Prediction: at least one incorrect mapping in a directed two-request reversal and nonzero errors in seeded discovery and holdout. Control: record (VA,PA) at the same translation point and compare with an independently computed mapping.

Hypothesis H115B: post-coalescer request count is not a lane-event count. Prediction: eight naturally aligned 4-byte lanes in one 32-byte line produce one aggregate request under the simplified line coalescer.

Hypothesis H115C: a source-pinned, fail-closed patch can record (VA,PA) at Vortex MMU translation without assuming a one-to-one issue/egress join. Prediction: all five source anchors are unique at pinned Vortex SHA. Actual simulator compilation is a separate gate.

Controls: fixed seeds 115001/115002/115003; discovery 256, holdout 128, minimally guided probes 48; independent C++ enumeration over 36 combinations. No simulated GPU cycles, RTL PPA or silicon results.

Cheapest discriminating next test: compile pinned Vortex with optional MMU probe and run two VPNs with TLB miss/hit under a multi-CTA workload. Compare tagged physical mappings against an independently dumped page table; check fault and bypass events separately.
