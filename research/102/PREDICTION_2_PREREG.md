# Preregistered follow-up prediction, frozen before test
Discovery showed a balanced-branch bank service cliff: baseline masked groups request 2 reads/bank; regrouped 32-lane groups request 4 reads/bank under the fixed mapping. With positive migration/setup overhead, predict strictly worse compacted service at RF ports <=3, strictly better at >=4, for previously untested lengths 12 and 24, warps 8 and 16, window 4 and 8, banks 16, migration bandwidth 8, setup 4 and no memory instructions.
This document mistakenly calls these 16 combinations per category; executable product is 2 warps x 2 windows x 2 lengths x 7 ports = 56. Keep bookkeeping mistake visible.
This is a within-model sign prediction, not silicon speedup or architectural novelty.
