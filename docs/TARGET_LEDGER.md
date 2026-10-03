# Target and evidence ledger

## Reference envelope

RTX 5090 is a comparison target, not an implementation template. NVIDIA's public product specification currently lists 21,760 CUDA cores, 2.41 GHz boost, 3,352 AI TOPS, 318 RT TFLOPS, 32 GB GDDR7, 512-bit memory interface, PCIe Gen 5 and 575 W total graphics power.

## Gate state

| Gate | State | Evidence |
|---|---|---|
| FP32 issue arithmetic | INCONCLUSIVE | executable issue model; realistic pipeline absent |
| Matrix issue arithmetic | INCONCLUSIVE | unit issue model only |
| Memory | INCONCLUSIVE | target only |
| Graphics/raster | INCONCLUSIVE | not implemented |
| Ray traversal | INCONCLUSIVE | not implemented |
| Software execution | INCONCLUSIVE | not implemented |
| Frequency | INCONCLUSIVE | 2.56 GHz target only |
| Area | INCONCLUSIVE | no synthesis |
| Power | INCONCLUSIVE | 575 W ceiling only |
| Overall | INCONCLUSIVE | broad gate intentionally unmet |

## Next decisive experiment

Implement dependency-aware Wave32 scheduling and a banked register-file traffic model. Compare a monolithic RF baseline with the proposed operand-cache hierarchy on deterministic compute, divergence and reuse traces. Preserve the hypothesis only if RF traffic falls without unacceptable scheduler stalls.
