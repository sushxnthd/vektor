# Vektor-120 preregistration — pinned MMU compilation and trace provenance

Date: 2026-10-12. Classification: CAPABILITY-BUILDING / DISCRIMINATION.

## Claim under test
The V115 source-pinned MMU VA/PA instrumentation can compile with VM enabled in the actual public Vortex SimX build. This has **not** previously been established; passing source-anchor checks alone is insufficient.

## Prediction (registered before execution)
P1: checkout `vortexgpgpu/vortex@7fe19369587c087f902c3e2bc2add612aa910a95`, apply the V115 patch, enable `VX_CFG_VM_ENABLE`, and compile the patched MMU translation unit with the upstream build system. A successful object build demonstrates *compilability only*, not full simulator correctness.
P2: a source-anchored test rejects an unpinned checkout or changed source anchors.
P3: a full simulator build may fail on unrelated upstream dependencies; preserve full logs and classify that separately.

## Discriminators
- Compilation fails at injected code: falsifies source compatibility; fix minimally, re-run.
- Compilation passes but full simulator fails: partial capability milestone, no runtime validation.
- Full simulator executes but records no events: instrumentation coverage is unproven.
- Real VA/PA trace available: next test must compare emitted events to independent request-accounting and trace identities.

## Controls / boundaries
No hardware PPA or performance claims. Do not infer GPU memory ordering or RTX 5090 progress from an MMU compilation. Preserve exact upstream SHA, compiler, flags, logs, and runner. Zero paid services.

## Next decisive action
Run the CI source-pinned VM-enabled compile; inspect build output and address any patch-specific errors.