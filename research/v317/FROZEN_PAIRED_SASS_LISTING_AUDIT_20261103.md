# Frozen V317 paired compiled-SASS listing audit (2026-11-03)

## Question and evidence tier
Can the existing conservative lexical source-register auditor survive contact with two independently published, compiler-produced **sm_80 Triton SASS listings**, and can any resulting static count comparison justify a bank-scheduling claim? The original binary, exact compiler/tool version, dynamic counts, bank mapping and RF-cache behavior are **not available**. Thus these are third-party *unverified binary-provenance listings*, not RTX 5090 evidence.

Pinned published sources (gist revision, not floating HEAD):
- fast.sass: https://gist.github.com/shunting314/90f35fd6ccc905a9ff3124e1c0a6dfad/raw/dd1b8a74e5ca6b5bddfde09065650371486b0675/fast.sass
- slow.sass: https://gist.github.com/shunting314/157c1a01e8c37bbd8d707ba1b8f038f9/raw/31f9e57dd456ef54b396cfe1b576ed63712bd0e7/slow.sass

## Frozen protocol, before calculating outcomes
1. Download each raw text listing unchanged, record byte count and SHA256. Verify both declare sm_80 and the same named kernel. Reject truncated/HTML content.
2. Run `research/v317/sass_audit.py` on each listing unchanged; record total instruction lines, classified/unknown/unparsed, static source occurrences and .reuse hints. Report static **per-instruction** normalized counts as well as totals, with no dynamic weighting.
3. Independent checker must count PC-prefixed instruction lines using a separate regex and check instruction accounting. Any unknown opcode or unparsed candidate is **missing information**, not zero RF demand.
4. Freeze *no numerical speedup prediction*. Predict that neither source alone can identify physical bank conflicts or dynamic scheduling throughput; a nonzero unknown-semantics fraction will invalidate any whole-kernel RF-read total.
5. Compare listings only as a parser transfer/falsification and potential compiler-difference case study; labels fast/slow are publisher filenames, not independently measured timings. Do not copy third-party SASS listings into the repository.
6. Kill the source-count-to-GPU-throughput inference if dynamic execution frequencies, cache hits, physical bank mapping, or binary verification are absent. Preserve previous V317 area/electrical falsifications. No new controller promotion.

## Reproduction
A new standard-library-only script will fetch pinned URLs, run the existing parser, and emit machine-readable JSON; an independent checker will validate the accounting. The offline run may use externally fetched raw text without claiming its own binary verification.
