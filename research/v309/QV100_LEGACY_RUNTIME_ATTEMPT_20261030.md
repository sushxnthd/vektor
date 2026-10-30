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
