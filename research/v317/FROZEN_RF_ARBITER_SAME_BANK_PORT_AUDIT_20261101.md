# Frozen RF bank-port accounting audit (2026-11-01)

Status: protocol frozen before the new checker, results, or RTL edits. This is an independent *baseline-validity* audit within V317, not a newly promoted GPU architecture mechanism. Existing PR #34 and its branch remain the only active Vektor research vehicle.

## Hypothesis and falsifier

The existing `rtl/vtile/rf_bank_arbiter.sv` admits a request with `src0_bank == src1_bank` while charging one bank read. Bank indices alone do **not** establish operand identity, and therefore cannot justify physical read sharing. Under the explicit conservative model of two independently required operand reads per instruction and two read ports per bank per cycle, such a request must consume two ports. A same-bank pair granted concurrently with another request to that bank is a physical overgrant if total demanded reads exceed two. A separately proven identical-operand or multicast path would change this premise, but the current arbiter has no operand IDs or proof input.

## Predeclared tests

1. Exhaust all 4-slot request-valid masks and all src0/src1 bank combinations for two banks (4,096 cases), with a Python translation of current RTL priority semantics and an independent per-bank read-count oracle.
2. Report number of cases with at least one overgrant, total overgranted slots, and minimal counterexample. Do not count this as a GPU speedup.
3. Compare conservative two-port greedy issue with the exact maximum-cardinality subset among the same four requests, using the same two read ports per bank and the same instruction inputs. Preserve fixed priority as a resource-identical control; exact maximum is an optimistic scheduling upper bound with uncosted selection logic.
4. Freeze a predicted failing regime: two valid requests both requiring two operands from bank 0. Freeze a predicted passing regime: two valid requests each requiring two operands from separate banks 0 and 1. Verify both before inspecting aggregate results.
5. Perform a second independent randomized four-bank test with fixed seed 31711 and 10,000 trials, including a direct RTL-model translation and independent oracle. All cases must be deterministic.

## Decision and evidence tiers

If overgrants exist, declare existing arbiter unsuitable as a physically credible baseline without either conservative double charging or an explicit, verified same-operand sharing predicate. If no overgrants exist, reject the hypothesis. This is a source-level semantic/port-capacity test only: no claim of RTL simulator success, synthesis, placed timing, power, real register-file semantics, or measured GPU throughput. Existing V317 forwarding no-go remains in force.
