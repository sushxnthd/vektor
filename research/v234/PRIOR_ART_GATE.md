# V234 prior-art gate — no breakthrough

Prior-art audit (20 October 2026):

1. Memento, ISCA 2024, DOI 10.1109/ISCA59077.2024.00075: adaptive compiler-assisted GPU register-file cache repurposes existing RF structures and schedules for reuse. Reports 46.4% fewer RF bank reads and 6.1% performance improvement in its evaluation.
2. BOW, MICRO 2020, DOI 10.1109/MICRO50266.2020.00084: bypasses repeated RF accesses in GPU operand windows and explicitly studies temporal reuse.
3. Malekeh, 2023 ACM workshop: lightweight register-file caching in GPU collector units.

V234's adaptive last-operand retention and its temporal-locality law are therefore NOT a new architecture concept. Synthetic tests confirm only a narrow analytical boundary against an offline static-pin oracle, not superiority to established adaptive GPU operand caching. Physical qualification is not available. The current Vektor tile is unchanged.

Disposition: RETIRE V234 as a breakthrough candidate. Preserve software results and blocked source-publication attempts. Next kernel must compare against prior-art-grade adaptive reuse, not only static pinning.

Source publication: GitHub safety checks blocked model.py, reuse_slot.sv and test_v234.py. Local archive holds source and results. No RTL simulation, synthesis, electrical STA or measured power.
