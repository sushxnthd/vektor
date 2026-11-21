# Independent periodic conservation execution — 2026-11-20

Protocol commit: `00a68b3cd6e6c561ddfe9b4b34352a1bb66a913a`; source blob: `45aacb1d107408c0c5b35c4fe98e0aa0aa57b5ef`.

A local Python 3.13.5 transcription of the 73-line checker was executed with exit code **0** and output:

```
PASS: 12 full-window periodic comparisons, per-cycle conservation, oldest protection and bank-port legality
```

**Reproducibility limitation:** this run transcribed the fetched GitHub source into a local script rather than executing a byte-for-byte downloaded source file. This establishes the tested logic passed, but does not constitute a byte-identical hosted run. Re-run the committed source verbatim in CI before claiming independent reproducibility. The 12 periodic cases are negative controls; equal throughput in these cases is not a universal upper bound. No RTL simulation, synthesis, electrically legal routing, SRAM integration or GPU IPC was produced. Previously measured compact-greedy area dominance and electrical illegality remain binding. Preserve one V296/V317 research mechanism; do not resurrect historical V287. No physical promotion of the oracle.
