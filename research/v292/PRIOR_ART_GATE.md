# V292 priority and realism gate (preliminary)

- SIMD lane permutation / dynamic compaction: Rhu and Erez, ISCA 2013, DOI 10.1145/2485922.2485953. V292 cannot claim invention of disjoint-mask compaction.
- GPU compression and wire energy: NVIDIA, *A Case for Toggle-Aware Compression for GPU Systems* (2016), https://research.nvidia.com/publication/2016-03_case-toggle-aware-compression-gpu-systems. Lower nominal payload need not reduce toggles or energy.
- GPU memory-sector coalescing is established. The first gate must confirm whether the L1-to-collector response is actually a 32-lane mask-addressable bus rather than full sector/line return, and whether two collectors accept data simultaneously.
- This RTL overlays two lane payloads on one existing bus. It **does not** compress a cache-line fetch from DRAM, save RF write ports, or prove higher warp issue throughput. Metadata requires two tags and two lane masks; if the original link cannot carry these bits at the same clock and width, equal-resource benefit is zero or negative.
- Strongest control must be allowed to exploit the same lane routing, queue and two collector destinations. If conventional packing matches, retire immediately.
- No complete prior-art audit or novelty claim.
