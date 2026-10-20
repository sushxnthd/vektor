# V252 analytical opportunity sweep (not performance evidence)

Four one-read banks, W ready requests, bank probabilities [s,(1-s)/3,(1-s)/3,(1-s)/3].
Expected number of distinct banks available to a perfect one-cycle matcher:
D(W,s) = sum_b (1 - (1-p_b)^W).
At W=8: s=0.25 -> D=3.599548; s=0.60 -> D=3.044488; s=0.85 -> D=2.009738; s=0.95 -> D=1.377428; s=1.00 -> D=1.000000.
This is a mathematical opportunity bound, NOT achieved throughput. The strongest equal-resource lookahead baseline has access to the SAME bank choices, so the sweep does not establish incremental advantage.
Next physical discriminator: compare one-cycle selection critical path, area, max-cap/slew and identical-buffer controls. Holdouts remain frozen; no tuning.
