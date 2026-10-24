#!/usr/bin/env python3
"""V296 preregistered *structural* crossover sweep, not a PPA prediction.
Counts comparator input-bit comparisons vs bank-decode output bits only.
Unknown physical coefficients and wiring can reverse this ranking.
"""
import json,math
rows=[]
for banks in (4,8,16,32,64):
    for slots in (2,4,8):
        reads=2*slots
        eq_pairs=reads*(reads-1)//2
        pair_bit_ops=eq_pairs*math.ceil(math.log2(banks))
        onehot_bits=banks*reads
        rows.append(dict(banks=banks,issue_slots=slots,operand_reads=reads,
            pairwise_equalities=eq_pairs,pairwise_comparator_input_bits=pair_bit_ops,
            onehot_decode_output_bits=onehot_bits,
            structural_ratio=round(pair_bit_ops/onehot_bits,6)))
print(json.dumps({"evidence":"E0 structural counts, NOT area/timing/power",
    "physical_coefficients":"unknown; not fitted",
    "rows":rows},indent=2))
