# V317: paired published sm80 SASS listings falsify lexical-count discrimination (2026-11-03)

**Evidence tier:** two publisher-hosted third-party Triton sm_80 SASS text listings, pinned by gist revision. **Not** independently checked against original cubins, nvdisasm version, execution traces, silicon measurements or RTX 5090. The raw listings were analyzed without copying their contents into Vektor. The existing V317 physical/electrical falsifications remain binding.

## Pre-outcome protocol
[FROZEN_PAIRED_SASS_LISTING_AUDIT_20261103.md](FROZEN_PAIRED_SASS_LISTING_AUDIT_20261103.md) was committed as `6bf9a4c` before collecting these paired statistics. Its predictions were *no valid GPU-speedup inference* and *nonzero unknown opcode coverage*, not a numerical speedup threshold.

The source listings, labeled `fast.sass` and `slow.sass` by their publisher, are from the same named sm_80 Triton layer-norm backward kernel:
- [fast.sass, pinned gist revision](https://gist.github.com/shunting314/90f35fd6ccc905a9ff3124e1c0a6dfad/raw/dd1b8a74e5ca6b5bddfde09065650371486b0675/fast.sass)
- [slow.sass, pinned gist revision](https://gist.github.com/shunting314/157c1a01e8c37bbd8d707ba1b8f038f9/raw/31f9e57dd456ef54b396cfe1b576ed63712bd0e7/slow.sass)

The labels are **not** independent performance measurements. The listed target is sm_80, **not** consumer Blackwell.

## Observed result
| Static property | Publisher fast | Publisher slow |
|---|---:|---:|
| PC-addressed instructions | 712 | 712 |
| Classified by existing narrow SASS lexical parser | 486 | 486 |
| Unknown instruction semantics | 226 | 226 |
| Parser coverage | 68.2584% | 68.2584% |
| Static lexical source-register occurrences (known opcodes only) | 848 | 848 |
| Static source occurrences per instruction | 1.19101 | 1.19101 |
| Static `.reuse` markers | 12 | 12 |
| Unique lexical source-register IDs | 75 | 75 |
| Instruction text differences at matched PC | 8 | 8 |
| First instruction encoding-word differences | 0 | 0 |
| Second control/encoding-word differences | 8 | 8 |
| Lexical register-token differences at matched PC | 0 | 0 |

The **eight** instruction-text differences are `LDG.E.EF.128` in the publisher-fast listing versus `LDG.E.128` in publisher-slow, at PCs `01a0, 01c0, 01e0, 01f0, 05b0, 05c0, 05d0, 05e0`. The first encoding word is unchanged, while the paired second control/encoding word differs. This observation alone does not establish the precise hardware semantics of `.EF`, cache behavior, or which listing runs faster.

The two files have **identical lexical source-register histograms**, so a ranking based only on the current static source-occurrence audit is mathematically unable to distinguish them, despite the eight observed encoded differences. The 226 unclassified instructions per listing make even the whole-kernel static RF-demand estimate incomplete. No physical bank mapping, RF-cache miss count, or dynamic execution weighting is available.

## Reproduction and independent checks
The pinned raw-text retrieval returned 162,587 ASCII bytes per file. SHA256 fingerprints of the retrieved text:
- fast: `987209a727aec2089969abc405a87d9714480f4617749e71f63aaa3b99d6c95f`
- slow: `9a3f845bcce6e9277201ad7337f250acc9ff12abca6e75df4acefe0e0173bac0`

The in-run independent structural comparison counted 712 distinct PCs per listing, matched every PC, and separately compared instruction text, both encoding words and register tokens. A separate lexical parser transcription produced the coverage/source counts above. These are **in-run checks**, not an assertion that the committed Python script ran against the full raw listings on a hosted runner.

The committed [reproducer](paired_sass_listing_transfer.py) downloads pinned revisions or accepts two offline files, calls the existing conservative [lexical parser](sass_audit.py), independently validates PC/encoding pairing, reports SHA256 and refuses mismatched PC sets. [Four synthetic structural tests](test_paired_sass_listing_transfer.py) passed locally. **Hosted full-listing reproduction passed**: [GitHub Actions #41551272415](https://github.com/sushxnthd/vektor/actions/runs/41551272415) completed successfully, checking both pinned text hashes, all 712 PCs, 486/226 opcode accounting, 848 source occurrences, 12 reuse hints, and the 8/0/8/0 instruction/first-word/control-word/register-token difference counts. This is reproducibility of a listing-level falsification, not validation of GPU speed or original binary provenance.

```sh
python3 -m unittest research.v317.test_paired_sass_listing_transfer
python3 -m research.v317.paired_sass_listing_transfer > /tmp/v317-paired-sass.json
# or use --fast /path/to/fast.sass --slow /path/to/slow.sass offline
```

## Scientific decision
**Falsify lexical source-count discrimination for this paired listing case.** The same 712 instructions, 848 known static source occurrences and 12 reuse markers coexist with eight encoded load-modifier/control differences. This is a *measurement-fidelity counterexample*, not proof that any Vektor scheduling mechanism improves real GPU throughput.

Do not fit a bank-conflict predictor to lexical SASS counts or promote a controller from these dumps. Before new physical RTL, obtain a cubin-pinned compiler/disassembler record, verified architecture target, dynamic workload frequency and bank/cache assumptions; then freeze predicted-win/no-win workloads and compare a physically legal matched-resource alternative. Preserve the prior V317 controller area/electrical kills and avoid RTX 5090-equivalence claims.
