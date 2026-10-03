# ISSUE-FP32-002

Classification: DISCRIMINATION + CAPABILITY-BUILDING.

Mechanism: replace the 556-bit exact simulation lattice with a bounded-width pipelined FMA implementation while retaining the exact reference as the correctness oracle.

Preregistered predictions: generic synthesis should complete within the CI budget; arithmetic mismatches, if any, should cluster around cancellation, subnormal, or rounding boundaries and must not be hidden by weakening the oracle.

World model: KNOWN — exact reference passes the frozen 10,008-vector suite. KNOWN — exact reference exceeded the 180-second generic synthesis budget. BELIEVED — bounded-width arithmetic is required for a scalable lane. UNTESTED — bounded implementation is bit-exact and physically useful.

Next decisive experiment: run identical generated vectors against exact and bounded implementations, cluster every mismatch by operand class/exponent separation, and synthesize the bounded lane. No frequency, area, power, or throughput claim until those gates pass.
