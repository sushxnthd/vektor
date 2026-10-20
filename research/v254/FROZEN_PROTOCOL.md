# V254 frozen protocol

Source: 2026-10-21 frozen research bundle. Mechanism: dual independently addressable 16-bit halves of a 64x32 register file; two narrow reads or one wide read per cycle; 32-bit total read data per cycle. Strongest equal-resource control: CORF++-style dual-addressable subbanks with identical physical resources. Positive holdout seed 254101: 8192 reads, q=0.8, balanced halves; negative holdout seed 254102: 8192 wide reads, q=0.0. Gain law for balanced placement: G <= r/(1-q/2), with r=f_split/f_mono. No architectural novelty or performance claim until independent physical PPA checks.

V153/V156 remain electrically disqualified. No integrated tile change.
