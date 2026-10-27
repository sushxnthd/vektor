# V296 fixed-word bank-local proof and hard nontransferability boundary (2026-10-27)

**Evidence tier: independently executed exhaustive software oracle, not hosted RTL or physical signoff.**

The new [independent proof checker](fixed_word_bank_local_proof.py) was executed in a local Python 3 environment before committing this report. It enumerates all **458,752** combinations of two 8-bit RF words and zero, one or two logical read requests to the same bank (7 request patterns × 65,536 word-data pairs). The original dynamic two-port priority addressing and the fixed-word port read return identical data in all cases.

It also enumerates **104,976** combinations of four request slots, eight source banks from a 3-bank subspace, and all 16 request-valid masks. An independently coded V296 pairwise admission reference admits 158,409 waves in aggregate and **never exceeds two operand reads per bank**. These are finite exhaustive microdomain checks, not full 16-bank formal equivalence of the complete RTL/scheduler.

**Hard falsifier outside the proved domain:** with three accesses to one bank, word selectors (0,0,1) and bank data (0,1), the old dynamic two-port logic (which saturates the second-port selection) would return (0,0,0), whereas fixed-word broadcast returns (0,0,1). A third request is illegal under the V296 two-port admission contract. This counterexample prevents silently extending the proof to three-port pressure, deeper banks, or arbitrary GPU RFs.

The fixed-word topology may reduce scheduler-to-operand capture delay only because the toy RF has **exactly two words per bank**. In a production bank with many words, hardwired word 0/word 1 ports are not sufficient. Even if the hosted mapped and physical tests improve, the result cannot be called a world-class or generalizable GPU architecture benefit without a deeper-bank/macro transfer.

The original physical signoff failure is unchanged. [Prospective protocol](FIXED_WORD_TWO_PORT_RF_CONE_PREREG_20261027.md), [new RTL](v296_tile_slice_fixed_word.sv), and [matched hosted workflow](../../.github/workflows/v296-fixed-word-cone.yml) remain the next decisive gates. No V287 revival, no new architecture mechanism, no Kernellum modifications, no GPU performance/power claim.

Reproduce: `python3 research/v296/fixed_word_bank_local_proof.py`. Compare its JSON stdout to `FIXED_WORD_BANK_LOCAL_PROOF_RESULT_20261027.json`.
