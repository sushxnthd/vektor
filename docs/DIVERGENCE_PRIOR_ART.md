# Divergence / Thread-Regrouping Prior-Art Boundary

Vektor must not claim dynamic thread regrouping, branch compaction, or compaction gating as novel. The following work materially overlaps the initial "dynamic cohort" idea.

## Closest established mechanisms

### Dynamic Warp Formation (MICRO 2007)
Wilson W. L. Fung, Ivan Sham, George Yuan, Tor M. Aamodt, **Dynamic Warp Formation and Scheduling for Efficient GPU Control Flow**. MICRO 2007. DOI: `10.1109/MICRO.2007.30`.

The paper dynamically regroups threads into new warps after divergent branch outcomes. It reports an average 20.7% improvement for dynamic regrouping in its evaluated system and estimates non-trivial hardware-area overhead. This is a direct collision with any generic Vektor claim of "regroup divergent lanes across warps."

### Thread Block Compaction (HPCA 2011)
Wilson W. L. Fung, Tor M. Aamodt, **Thread block compaction for efficient SIMT control flow**. HPCA 2011. DOI: `10.1109/HPCA.2011.5749714`.

TBC shares reconvergence state across warps in a thread block and compacts threads after divergence. The paper reports improvements over both per-warp reconvergence and Dynamic Warp Formation on its divergence-heavy benchmark set.

### CAPRI (ISCA 2012)
Minsoo Rhu, Mattan Erez, **CAPRI: Prediction of compaction-adequacy for handling control-divergence in GPGPU architectures**. ISCA 2012. DOI: `10.1109/ISCA.2012.6237006` / ACM DOI `10.1145/2366231.2337167`.

CAPRI predicts whether synchronization/compaction is likely to be worthwhile and bypasses compaction when it is not. Therefore a generic "only compact when expected benefit exceeds overhead" mechanism is also prior art unless Vektor introduces a materially different predictor, objective, scope, or mechanism and demonstrates that distinction experimentally.

### NVIDIA Shader Execution Reordering
NVIDIA publicly documents Shader Execution Reordering (SER) as on-the-fly thread reordering intended to improve execution and memory coherence, particularly in ray-tracing shaders. Modern Vektor work must therefore distinguish itself from both classic branch compaction and commercial reordering mechanisms.

### Vortex SIMT reconvergence baseline
Vortex exposes `split` / `join` control-flow operations around an immediate-postdominator-style reconvergence stack. This is an appropriate open reference point for a conventional SIMT baseline.

## Consequence for Vektor

The following are **baseline capabilities / prior art, not Vektor novelty claims**:

- per-warp masked execution and postdominator reconvergence;
- dynamically regrouping threads with the same branch outcome;
- thread-block-wide compaction;
- deciding whether compaction is adequate/profitable;
- reordering threads to improve execution coherence;
- generic memory-coherence hints for reordering.

The current `divergence_compaction_bound_v1` benchmark therefore uses bounded compaction only to establish an upper bound and to quantify the cost/benefit region before an implementation is attempted.

## Research gap to test instead

A defensible Vektor contribution would need a narrower mechanism that survives comparison with these baselines. Candidate directions must be tested rather than asserted. Examples worth falsifying include:

1. joint control-flow + memory-system scheduling under the explicit Vektor L1/L2/MSHR model;
2. a low-state hardware policy that approaches an oracle compaction decision while preserving cache-line locality and avoiding minority-thread starvation;
3. register-remap-aware scheduling that prices RF-bank movement and operand-cache disruption directly into regrouping decisions;
4. compiler/hardware contracts that mark reorder-safe regions and expose predicted locality without requiring programmer-inserted reordering calls.

These are research questions, not current novelty claims. A direct prior-art audit must be repeated before promoting any one of them.
