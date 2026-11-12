# V309: First complete source-pinned QV100-SASS workload simulation and independent counter audit (2026-10-30)

## Evidence identity and decision

The original preregistered smallest-complete-workload protocol **PASSED** in [hosted run 41091279796](https://github.com/sushxnthd/vektor/actions/runs/41091279796), head [01933a1](https://github.com/sushxnthd/vektor/commit/01933a14f2b31851fa7f80566e0eaf53b5a6fc5b). [Raw evidence artifact 12992914321](https://github.com/sushxnthd/vektor/actions/runs/41091279796/artifacts/12992914321), SHA-256 `9728ca510a69a1826a307aa5d68b7e13ba057396340bdaf3e18f685d47ffb390`. Artifact retention is 30 days; regenerate via the pinned workflow.

The authenticated Tesla V100 Rodinia 2.0-ft archive selects the original pathfinder `1000_20_5` command list: 4 kernel launches, 2 original MemcpyHtoD commands, 1,953,528 source bytes. Pinned Accel-Sim `7ba54ded60c4ba0083410c37d22d719166acd6dc`, GPGPU-Sim `4195dd4f229cbf03f4f38c49139ae94d01d23f03`, pybind11 `18bbe9d7c9b0009b992e812e1b59e7a0d4474dbd`, and container manifest `sha256:d963b1a0bccdb9ade23d19f184a17724c9adf2c8ec580fcbff76c3a9a2bad02a` were used. The build required recorded non-source-mutating dependency, include-path, compiler and linker flags. This is a **working simulator runtime**, not hardware validation.

Both complete runs exited 0, emitted the explicit GPGPU-Sim completion marker, and recorded four kernel completions. Each reported **28,717 aggregate simulated cycles** and **1,059,640 aggregate simulated instructions**. The run logs have different hashes because wall-clock simulation-rate text varies; the independently extracted per-kernel simulator counters match exactly.

## Independently reconstructed kernel increments

Each L1/L2 and global-memory count below is the **difference between consecutive cumulative simulator records**, not a direct per-kernel counter, a DRAM transaction count, or a byte measurement.

| Kernel launch | Sim cycles | Sim instructions | L1D misses | L2 misses | Global read counter | Global write counter |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7,294 | 276,480 | 917 | 128 | 789 | 156 |
| 2 | 7,295 | 276,480 | 915 | 1 | 787 | 156 |
| 3 | 7,231 | 276,480 | 915 | 0 | 787 | 156 |
| 4 | 6,897 | 230,200 | 787 | 0 | 658 | 157 |
| **Total** | **28,717** | **1,059,640** | **3,534** | **129** | **3,021** | **625** |

The first launch accounts for **128/129 = 99.22%** of reported cumulative L2 misses. The later two launches report zero additional L2 misses. This is a concrete simulator-workload nonstationarity observation, consistent with cache-state effects, but it **does not identify the cause** without controlled cold-cache/flush experiments and access-stream equivalence. The fourth launch also executes fewer instructions, so its shorter cycle count must not be interpreted as a performance improvement.

## Independent audit and falsification controls

[Independent parser](qv100_runtime_counter_audit.py) reads the two original raw simulator logs, requires the exit marker, exact four-launch linkage to the frozen selection manifest, strictly sequential launch UIDs, exactly one of each named counter per kernel record, nondecreasing cumulative counters, and exact per-kernel cycle/instruction conservation. It compares the full per-kernel counter vectors between repeats rather than trusting the runtime harness's final summary. Locally replayed against the downloaded artifact: **PASS**, with two positive and eight adversarial negative fixture controls.

- Repeat 1 raw log SHA-256: `fae56e0412b42fbdf2792c7811b261218e9c67e7a43bab91552f5a2615302abc`
- Repeat 2 raw log SHA-256: `db1d4a3e645a1451a11787a1cbdcd0f207e61d79a32a388a766ee270fad34c56`
- The [updated hosted workflow](../../.github/workflows/v309-legacy-qv100-runtime.yml) now reruns the independent audit after every successful source-pinned simulator build, and uploads the JSON and raw logs even when subsequent checks fail. [Hosted independent-gate recheck #41092244759](https://github.com/sushxnthd/vektor/actions/runs/41092244759) **PASSED**, including the fresh source-pinned build, both complete workload simulations, two positive and eight adversarial parser controls, and exact independent per-kernel counter replay. [New raw artifact #12995255077](https://github.com/sushxnthd/vektor/actions/runs/41092244759/artifacts/12995255077), SHA-256 `7048145df6c94e0e336880b86e5eae53dbd62df0306e43cf2f4a07fc01574ed5`.

## Boundary of the claim and next kill test

**Established:** one authentic historical command-list workload executes twice to completion under a source-pinned QV100-SASS simulator, and independent counter reconstruction reveals reproducible per-kernel cache-counter variation.

**Not established:** physical GPU cycles, actual V100 cache misses or DRAM traffic, simulator-to-hardware calibration, an implementable V309 architecture mechanism, matched-resource speedup, power, area, timing, or any RTX 5090 comparison. The simulated L1/L2 counter names do not define a bytes-per-miss conversion.

Next: reproduce the exact workload with an explicitly defined equal-resource control and an independently specified perturbation or calibration source; require repeated cycle/counter measurements and a preregistered win/no-win boundary. A mere cold/warm counter difference does not qualify as a new GPU mechanism. No retired V287/V296 candidate is revived.
