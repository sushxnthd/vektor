# V309 pinned QV100-SASS runtime attempt: build preflight failure (2026-10-30)

## Frozen experiment and evidence tier

The previously committed prospective protocol selected the smallest complete original Tesla V100 Rodinia 2.0-ft workload by uncompressed trace bytes, with all original memory-copy commands preserved. The source archive SHA-256 was authenticated before selection. This report records the **negative hosted result** before modifying the build workflow; it does not redefine workload selection or the performance acceptance criterion.

- Source: [GitHub Actions run 41083970431](https://github.com/sushxnthd/vektor/actions/runs/41083970431), head `71bb52a1663de92da1a126e1fbaec5e008e656a6`, failed.
- Raw evidence: [artifact 12990693386](https://github.com/sushxnthd/vektor/actions/runs/41083970431/artifacts/12990693386).
- Independent selection and malformed-input tests: PASS.
- Original archive SHA-256 verification: PASS.
- Selected command list: `rodinia_2.0-ft/9.1/pathfinder-rodinia-2.0-ft/1000_20_5___data_result_1000_20_5_txt/traces/kernelslist.g`.
- Selected source payload: 1,953,528 uncompressed bytes, 4 original kernel launches, 2 `MemcpyHtoD` commands.
- Pinned upstream Accel-Sim `7ba54ded60c4ba0083410c37d22d719166acd6dc`, GPGPU-Sim `4195dd4f229cbf03f4f38c49139ae94d01d23f03`, pybind11 `18bbe9d7c9b0009b992e812e1b59e7a0d4474dbd`.
- Container manifest digest observed: `sha256:d963b1a0bccdb9ade23d19f184a17724c9adf2c8ec580fcbff76c3a9a2bad02a`.
- Fatal error: `bash: line 14: nvcc: command not found`, exit 127, in build provenance collection **before** `source gpu-simulator/setup_environment.sh` and **before** `make`.
- Result: **BUILD_PREFLIGHT_FAIL**, no simulator binary demonstrated, no simulator cycles, no memory counters, no architecture performance data.

## Root-cause scope and repair

The workflow exported `CUDA_INSTALL_PATH=/usr/local/cuda-11.0` but never prepended `$CUDA_INSTALL_PATH/bin` to `PATH` before invoking `nvcc --version`. This is a directly observed *PATH omission* and is consistent with the image's published CUDA-toolkit setup. It is not evidence of an absent CUDA installation. The repair must explicitly verify the executable at the pinned path and export PATH, then attempt the same source-pinned build and same frozen workload; a new failure must be preserved rather than declared success.

The old Docker tag `latest` is also mutable. Reuse the exact observed container manifest digest in the next attempt.

## Decision

This failure is a reproducible negative result at the **build-preflight** tier, not a falsification of any architecture mechanism or of the selected workload. Keep the existing research branch and draft PR, preserve the frozen workload and kill criteria, and do not promote V287/V296 or claim a GPU speedup. If a corrected build reaches simulator execution, require two complete runs and nonzero cycles/instructions with explicit simulator exit markers. Further physicality claims require matched-resource RTL, synthesis, timing, electrical and bandwidth evidence.

## Second hosted attempt: shell strict-mode incompatibility

- [GitHub Actions run 41088025400](https://github.com/sushxnthd/vektor/actions/runs/41088025400), head `e8c13640a86312c80c7c6cf209323977e3e0c238`, **FAILED** after the CUDA PATH fix.
- [Raw artifact 12992053553](https://github.com/sushxnthd/vektor/actions/runs/41088025400/artifacts/12992053553).
- The digest-pinned container was pulled successfully; `nvcc` preflight passed; all source-pinned repositories were checked out. The next failure was `gpu-simulator/setup_environment.sh: line 93: GPGPUSIM_SETUP_ENVIRONMENT_WAS_RUN: unbound variable` under the workflow's `set -u`.
- The upstream script directly expands a potentially unset variable and is not nounset-safe. Temporarily disable `nounset` *only while sourcing this external setup script*, then re-enable it before build and simulation. Preserve `errexit` and `pipefail` throughout.
- Result: **ENVIRONMENT_SETUP_FAIL**, before compilation. No simulated cycles or hardware performance observations. This does not falsify the architecture.

## Third hosted attempt: missing zstd development headers

- [GitHub Actions run 41088538480](https://github.com/sushxnthd/vektor/actions/runs/41088538480), head `817150e58fe2bede088b46413fbddb4d04c21acc`, **FAILED** after successful CUDA preflight and successful upstream environment setup.
- [Raw artifact 12993630232](https://github.com/sushxnthd/vektor/actions/runs/41088538480/artifacts/12993630232).
- The actual source-pinned `make -j2 -C gpu-simulator` began compiling `trace_parser.cc` and `trace_driven.cc`. Both stopped on `fatal error: zstd.h: No such file or directory` from `trace-parser/warp_trace_stream.h`. Make exited 2. The pinned upstream source includes a `.tracez` streaming reader requiring libzstd development headers, even though the selected original workload uses `.traceg`.
- Result: **COMPILER_DEPENDENCY_FAIL**, before any simulator binary or runtime. The next attempt may install the system `libzstd-dev` package inside the same digest-pinned container; its version and package provenance must be recorded, and no unverified cycles may be reported.

## Fourth hosted attempt: upstream header-search-path regression

- [GitHub Actions run 41088946031](https://github.com/sushxnthd/vektor/actions/runs/41088946031), head `a8aed38f46b007edcae23f2e86a91498defccc8e`, **FAILED** in C++ compilation.
- The pinned CUDA 11 container successfully installed `libzstd-dev 1.3.3+dfsg-2ubuntu1.2`, passed upstream environment setup, and began compiling the trace reader. The next error was `fatal error: tracez_format.h: No such file or directory` in `gpu-simulator/trace-parser/warp_trace_stream.h`.
- An immutable upstream tree inspection located `tracez_format.h` at `util/tracer_nvbit/tracer_tool/tracez_format.h` in the **same pinned Accel-Sim commit**; it is absent from the simulator's default include search paths. This is a source-tree/include-path integration defect, not missing trace data or a GPU measurement.
- Proposed non-source-mutating repair: export `CPLUS_INCLUDE_PATH=/tmp/accel/util/tracer_nvbit/tracer_tool` during compilation and preserve the upstream source revision unchanged. Re-run the exact same frozen input and completion gate. Result tier: **COMPILER_INCLUDE_PATH_FAIL**.
