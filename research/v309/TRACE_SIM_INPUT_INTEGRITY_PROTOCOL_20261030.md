# V309 trace-to-simulator input integrity protocol (frozen 2026-10-30)

Archive: Purdue Tesla V100 Rodinia 2.0-ft 2020-03-18, SHA256 aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1.

Predeclared gate: count all .traceg members, kernelslist.g command lists, kernel launches, memcpy commands; resolve launch targets within their own directory, reject unsafe/ambiguous/missing/duplicate references, report unreferenced traces. A strict pass requires zero missing, ambiguous, duplicate or unreferenced targets, with all links resolved locally. Test independent synthetic valid and malformed fixtures. Sample bounded trace prefixes without claiming parser compatibility.

Fail closed on archive digest change, malformed input or missing trace linkage. Passing establishes only trace command-list identity, not Accel-Sim runtime compatibility, matched hardware counters, GPU cycles, physical RTL or speedup. Do not promote V287/V296; keep V309 PR #26 and Kernellum untouched.
