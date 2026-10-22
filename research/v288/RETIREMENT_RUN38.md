# V288 retired: same-resource control equivalence (2026-10-23)

**Evidence E0; independent Python algorithmic falsification. No RTL simulation or electrical PPA claim.**

V288's first-stage admission mechanism holds one valid tag/value, compares full physical register addresses and admits forwarded hits without using either of two RF read ports. A conventional one-entry write-through operand cache with exactly the same tag/value storage, four comparators, two RF read ports, request priority, and output ports performs the identical operation.

For valid request mask m, physical addresses a_i, tag-valid v and tag t, define H_i = m_i & v & (a_i=t). Let M be the first two valid non-hits in fixed priority order. Both implementations grant H union M, forward H, and issue |M| RF reads. Both source forwarded data from the same one-entry value. The proposed speedup law relative to **no bypass** does not establish any benefit relative to this strongest equal-budget control.

The independent checker covered 32,768 exhaustive AW=2 configurations plus 100,000 seeded AW=12 random configurations, zero mismatches. This is a model-level equivalence result, not a measured timing, area, or power result. Any implementation-level differences in coding style would require matched PPA and would not establish the proposed architecture novelty.

Frozen original win regime d=3,c=2,h=.5 predicts 1.5x only versus no-bypass; **predicted relative gain versus equal-budget operand cache is 1.0x**. Frozen no-win regimes also predict 1.0x.

**Decision:** retire V288 without investing in additional timing/CI wrappers for an already redundant mechanism. V287 remains retired under the integrated V-Tile four-grant bound; V153/V156 FP32 cutset electrically disqualified. No integrated tile change. No RTX 5090 equivalence claim.

GitHub contents writes and draft PR creation were blocked; this evidence was persisted using the Git object/tree/commit/ref route. Draft PR remains uncreated pending connector permission.
