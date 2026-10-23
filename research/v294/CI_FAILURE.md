# V294 first-attempt CI failure (preserved)

Workflow: https://github.com/sushxnthd/vektor/actions/runs/39886021210
Commit: c9ea6c17eb4c48e48c8aa597e7033149da552d4b
Outcome: **failure**. Icarus directed holdouts and independent Python oracle passed. Generic Yosys control synthesis was marked **cancelled**; lookahead synthesis and artifact upload were skipped. No cell counts may be inferred from this failed run.

One repair replaced the dynamically indexed occupancy array with 16-bit occupancy masks, preserving bank capacity semantics. The repaired run https://github.com/sushxnthd/vektor/actions/runs/39886185175 completed successfully (1,480 control and 2,217 lookahead generic cells). This is the only physicality repair for V294. V294 remains retired on equal-budget policy equivalence.
