# Vektor-115 — MMU translation provenance

Vektor-114 found that pre-MMU virtual addresses alone cannot establish physical aliasing. Vektor-115 tests the next trap: a naive FIFO join of virtual-address issue records to physical-address MMU records can be wrong if request keys repeat and outputs reorder. The source-pinned probe emits virtual and physical addresses together at translation, without pretending to recover per-lane provenance after coalescing.

Reproduce with Python 3 and g++ (no GPU or paid service):

    cd research/115
    python3 test.py -v
    python3 trace_model.py
    c++ -std=c++17 -O2 -Wall -Wextra -Werror replica.cpp -o /tmp/v115_replica
    /tmp/v115_replica

To apply the optional probe to an independently obtained pinned Vortex checkout:

    python3 research/115/patch_vortex.py /path/to/vortex

Required upstream commit: 7fe19369587c087f902c3e2bc2add612aa910a95. The patch rejects missing/duplicate anchors and any other checkout revision. Set VEKTOR_MMU_TRACE to a writable CSV file to enable logging. CSV columns: seq,port,uuid,hart_id,tag,event,va,pa. T=TLB-hit forwarded, H=TLB-miss translation queued for replay, B=bypass forwarded, F=fault/killed (PA field is **not valid**). The H event is not proof of downstream forwarding. MMU request records may represent coalesced memory lines, **not individual lanes**. This is neither an architectural retirement trace nor DRAM traffic. Patched full Vortex compilation and execution are not yet established.

Main remains stable; research branch only. No proprietary RTL or leaked materials.
