# Vektor-072 — bounded replay-source closure and router drain

Date: 2026-10-10. Cost: $0. Parent: research/bounded-router-conservation-071 at 733bba44620dc101b68fc73b840b7d80b54841ad.

## Mechanism and preregistered predictions

The replay-source FIFO freezes admissions on a fence request, drains accepted packets, then registers fence_ack. The Vektor-071 router separately counts physical copies. UID reuse requires both producer closure and downstream packet extinction.

P1: source-only retirement permits stale delivery after UID reuse. P2: source closure plus physical-copy drain prevents stale delivery in the bounded two-epoch model. P3: independently written C++ and Python implementations agree on exact state/edge counts. P4: RTL rejects late replay admissions, drains under backpressure and allows same-UID reuse after a combined fence. P5: producer closure alone can coexist with queued router copies.

## Results and residuals

Software-model evidence: safe policy explores 148 states and 389 transitions with no stale delivery. Unsafe policy yields a seven-event counterexample after 100 states and 221 transitions. Independent C++ matches both counts exactly (zero residual). Twelve minimally theory-guided probes over queue capacity 1–4 and admission budget 1–3 preserve the policy ranking. With admission budget 1, capacities 2–4 are structurally equivalent: 48 states and 102 transitions each. These are finite atomic-event models, NOT RTL formal proof.

Shortest counterexample: admit E0 ACK; freeze source; emit old packet into fabric; source fence ACK; retire E0 prematurely; reuse UID0 in E1; deliver old E0 ACK. This falsifies source-only quiescence.

RTL candidate: research/072/rtl/replay_source_072.sv, integrated with research/071/rtl/bounded_fabric_071.sv. Testbench: research/072/rtl/tb_replay_fence_072.sv. RTL simulation, synthesis and physical PPA remain pending until tool output confirms them.

## Discovery Protocol V2 world model

KNOWN (bounded software): the dual condition prevents stale credit in the enumerated model; the unsafe policy has a concrete counterexample; independent model counts agree.
BELIEVED: registered source closure and counted physical-copy retirement can support finite tag reuse when all replay sources are enumerated.
CONFLICTING: early reuse improves occupancy but breaks safety; delayed reuse protects safety at possible throughput cost.
FALSIFIED: sender closure alone proves downstream ACK extinction; Vektor-071 also falsified resampling backpressured cloned requests.
ANOMALOUS: capacities 2–4 are structurally equivalent at one admitted packet per epoch.
UNTESTED: bypass replay, multi-hop NoC, cross-domain reset, asynchronous loss, liveness, unbounded proof, physical timing/area/power and GPU performance.

Adversarial roles: Explorer proposed source-fence RTL; Skeptic identified hidden replay and downstream copies; Experimentalist built the seven-event counterexample; Analyst kept claims model-scoped; Anomaly Hunter found the capacity equivalence; Prior-Art Auditor classifies this as standard quiescence/epoch logic without novelty claim; Replicator wrote independent C++; Theorist states the minimal rule: no old-epoch packet may remain capable of reaching a receiver when a finite identifier is reused.

## Reproducibility and limitations

Run Python: python3 research/072/model/formal_072.py
Compile C++: g++ -std=c++17 -O1 research/072/model/replicate_072.cpp -o /tmp/r072
Run: /tmp/r072
Compile RTL: iverilog -g2012 -s tb_replay_fence_072 -o /tmp/tb072 research/071/rtl/bounded_fabric_071.sv research/072/rtl/replay_source_072.sv research/072/rtl/tb_replay_fence_072.sv
Run RTL: vvp /tmp/tb072
Generic synthesis: yosys -Q -p 'read_verilog -sv research/072/rtl/replay_source_072.sv; synth -top replay_source_072; stat'

Single next decisive experiment: verify RTL simulation and generic synthesis, then inject an independent replay producer and asynchronous reset across a two-hop router. Require end-to-end packet conservation before further throughput optimization.

## External target and gates

NVIDIA official reference checked 2026-10-10: RTX 5090 has 21,760 CUDA cores, 2.41 GHz reference boost, 32 GB GDDR7, 512-bit memory, 575 W board power, fifth-generation Tensor and fourth-generation RT cores. Theoretical 1,792 GB/s follows from 28 Gb/s GDDR7 times 512 bits / 8. Public AI TOPS and RT TFLOPS are workload/precision-specific metrics, not FP32 or universal RT measurements.

Vektor-1A 160 tiles, Wave32, 128 FP32 lanes/tile, 2.56 GHz, two matrix engines/tile, 128 MB L2, 512-bit GDDR7, <=575 W and <=750 mm2 remain hypotheses. FP32, tensor by datatype/sparsity, memory capacity/bandwidth/cache, texture/raster, ray workloads, power/area/frequency and KPX software gates all INCONCLUSIVE. No RTX 5090-class equivalence claim.

Source: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/
