# FP32-MUL-RTL-004

Classification: **DISCRIMINATION + CAPABILITY-BUILDING**

Preregistered prediction: the bounded tuple frontend matches an independently expressed RTL test contract for >=20,000 deterministic triples and generic Yosys synthesis completes within 180 seconds.

Controls cover signed zero, subnormal/normal boundary, maximum finite, infinities, sNaN/qNaN; random triples use fixed seed 0x5090cafe. This validates only classification/sign/exponent/significand and 24x24->48 exact multiplication, not fused alignment, normalization, RNE packing, flags, timing, area or power.

Interpretation: simulation failure falsifies the tuple RTL contract; simulation pass plus synthesis timeout preserves functional credibility but rejects the implementation/tool path; both passing promotes the bounded multiply frontend to RTL-validated capability and makes bounded alignment/accumulation the next discriminator.
