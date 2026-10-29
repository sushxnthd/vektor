# V309: frozen V100 real-trace acquisition gate (2026-10-30)

**Frozen before downloading or inspecting archive contents.** The earlier 512 MiB limit applies to downloaded trace bytes; this one-time archive is independently listed at about 20 MiB. This is an evidence-acquisition experiment, not a new architecture mechanism.

## External source and target
- Source: Purdue Accel-Sim archive index, `https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/`.
- Exact archive: `rodinia_2.0-ft.tgz`, listed at **20M** on the public index. Hardware generation: Tesla V100, **not** RTX 5090, Hopper or Blackwell.
- Historical trace collection, not prospective workloads. No paired Nsight Compute counters have yet been established for this archive. Never claim any GPU speedup or calibrated stall attribution from these data.
- Companion literature: Accel-Sim (ISCA 2020), plus Accel-Sim tracer documentation. The 2026 H200 release has larger full configurations; this older V100 archive is a low-cost *format and trace availability* qualification, not a replacement for modern validated traces.

## Frozen acquisition/analysis
1. Download **only** this one archive in a disposable hosted runner, capped at 64 MiB of transferred compressed data. Record exact SHA-256, downloaded bytes, member count, declared trace bytes and archive member paths.
2. Never extract files to the filesystem. Reject unsafe paths, symlinks, device members, corrupt archives, oversized members, and malformed format.
3. Sample at most the first 24 trace members in tar order, at most 32 KiB each. Record first six complete text lines, count old-NVBit-format row prefixes, and hash each sampled prefix. Do **not** extrapolate sampled row counts to whole-workload dynamic statistics.
4. Independent local tests must reject traversal, corruption, no-trace archives, and unrecognized trace format. Preserve JSON artifact even if the format gate fails.
5. Qualification outcomes: `NO_TRACE_MEMBERS`, `TRACE_FORMAT_UNRESOLVED`, or `AUTHENTIC_TRACE_PREFIXES_ONLY_NOT_PERFORMANCE_VALIDATION`. All are evidence tiers, **none** promotes hardware.
6. If accessible, freeze archive SHA-256 for subsequent full parsing. Next stage requires independent family selection, a dynamic trace decoder, matched hardware counters or honest missing-counter caveat, and a prospective win/no-win workload freeze before proposing hardware.

## Non-interference and kill conditions
Keep the sole V309 qualification branch and draft PR #26. V287/V296/V297-V308 stay retired; no speculative scheduler is reactivated. No Kernellum writes. Do not call static PTX register-demand arithmetic a physical GPU bottleneck. If archive is inaccessible, malformed or contains no interpretable trace rows, preserve the failure and do not claim dynamic SASS evidence.
