# V296 matched-absolute-time bank/memory workload: prospective synthetic transfer protocol (2026-10-25)

**Evidence tier: synthetic discrete-event simulator, not GPU workload measurement, RTL physical closure, or a new architecture mechanism.** V296 remains the only active candidate. V287 stays retired. Do not unseal the pre-existing GPU workload holdouts or modify Kernellum PR #119.

## Why this is necessary

Earlier per-cycle synthetic replay compared identical request sequences at different *assumed* clocks. That makes the faster implementation receive more requests per real second and is not a fair fixed-real-time workload comparison. This protocol adds a **single timestamped workload shared by both contestants**. It explicitly models two RF reads per admitted wave, 16 banks, 2 read ports per bank, four priority slots, finite per-slot FIFO depth 8, and a shared 8-byte/wave bandwidth token bucket. An independent exhaustive 2^4-subset priority oracle must agree with the greedy selector each cycle; FIFO and byte conservation must pass. V296 and serial implement identical same-clock decisions, so any modeled advantage can arise only from *assumed* period differences and resource effects, not a new admission mechanism.

Use **hypothetical** tile periods serial=4 ns, V296=3 ns solely to stress a conditional model. Neither period has been physically achieved. Freeze workload generation: absolute time 60,000 ns, first 12,000 ns burn-in; one potential arrival per slot in each 4 ns interval, Bernoulli p=0.95, hotspot probability 0.35, hotspot persistence 0.90, two independent operand-bank draws per wave, 8 bytes per wave. Each contestant receives identical event timestamps and bank operands, with identical queue depth and memory-bandwidth policy. Never convert extracted negative setup slack to frequency.

## Calibration (used only to freeze predictions)

Seed 296101, 20 GB/s, 64-byte token bucket: matched-time throughput ratio 1.1922401 (conditional synthetic win, substantially below the naive 4/3 clock ratio). Seed 296102, 1 GB/s, 64-byte bucket: ratio 1.0000000 (bandwidth-limited no-win). Seeds 296103 and 296104 at 2.5 GB/s with 16-byte and 128-byte buckets respectively: both ratio 1.0000000. These are simulator outputs, not physical GPU measurements.

## Frozen prospective transfer: do not inspect until this protocol is committed

Use independent seeds 296201, 296202, 296203, 296204 with the same respective bandwidth/bucket conditions. Predict:
- Seed 296201 (20 GB/s): V296/serial throughput ratio in **[1.15, 1.23]** (predicted win conditional on a feasible 3 ns clock).
- Seed 296202 (1 GB/s): ratio in **[0.995, 1.005]** (predicted no-win).
- Seeds 296203 and 296204 (2.5 GB/s; 16 and 128 byte buckets): ratios in **[0.995, 1.005]** (bandwidth-bound, independent buffer sensitivity).
- The offered waves/ns must be exactly equal across implementations for every case, all exhaustive-oracle and conservation checks must pass, and measured traffic must not exceed sustained bandwidth.

**Failure policy:** If any frozen range, matched-arrival check, independent oracle, or conservation check fails, report the failed prediction; do not widen thresholds or change seeds. Do not interpret success as real GPU evidence. The original matched integrated physical implementations are BOTH_INFEASIBLE at 3.5 ns, and the strongest equal-resource serial control has not closed timing. The real performance claim stays falsified until independently validated integrated clocks, bandwidth/traffic and workloads exist.

Reproduce with `python3 research/v296/matched_walltime_workload.py --self-test`, `--evaluate calibration`, then `--evaluate prospective`. Preserve the original results and do not overwrite prior physical gates.
