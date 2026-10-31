# V309 frozen QV100 legacy trace-driven runtime gate (2026-10-30)

## Prior evidence and selection

The authenticated Purdue Tesla V100 Rodinia 2.0-ft trace archive is https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz, SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`. Existing linkage audit verified 210/210 trace references and all 351 HtoD memory-copy records. No original trace producer revision or hardware counters are authenticated.

Before inspecting simulation outcomes, select the **smallest complete workload directory** by total uncompressed sizes of its listed trace files, with lexical path tie-break. Require exact same-directory trace linkage; retain original `kernelslist.g` bytes, every listed kernel, and all memory-copy commands. Refuse archive digest drift, tar links/path traversal, duplicate members, missing references, or a 96 MiB extracted workload cap. Record all selected file hashes. This deterministic size selection is for a bounded smoke experiment, not a representative performance sample.

## Predeclared runtime and falsification

Attempt a complete unmodified trace-driven Accel-Sim simulation **twice** under the same QV100-SASS configuration, with 240-second cap per repeat, retaining raw simulator logs, process exit codes and any cycle/instruction/memory counters actually emitted. Source pins: `accel-sim/accel-sim-framework@7ba54ded60c4ba0083410c37d22d719166acd6dc`, `accel-sim/gpgpu-sim_distribution@4195dd4f229cbf03f4f38c49139ae94d01d23f03`, `pybind/pybind11@18bbe9d7c9b0009b992e812e1b59e7a0d4474dbd`. Record container image digest and build/toolchain provenance; no GPU is required for replay.

**PASS_RUNTIME** requires two exit-zero executions with a positive `gpu_tot_sim_cycle` and positive `gpu_tot_sim_insn` each, plus an explicit parser-completion signal. Do not assume a process exit is proof of full execution. Report cycle variation; a nonzero difference does not silently fail or disappear. A build failure, trace incompatibility, timeout, missing completion marker or absent counter is **FAIL_CLOSED** and the complete raw evidence must remain available. A failed run is not a throughput result.

This gate tests only whether the old source-attested input can actually run under the declared simulator. No architecture optimization is enabled. **Do not claim** matched hardware calibration, memory-traffic accuracy, RTL timing/area, power or speedup. V287 and V296 remain historical, V309 is qualification-only, and Kernellum PR #119 must not be touched. A passing runtime gate precedes any resource-matched hardware mechanism experiment; it is not itself a physicality pass.
