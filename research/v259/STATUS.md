# V259 frozen hypothesis

Sole active mechanism: use otherwise idle integer ALU slots to regenerate compiler-certified lane constants when RF banks are saturated. No extra RF ports or ALUs.

Analytical law: m=min(max(D-R,0),eD,A), ideal gain <= min(D,R+m)/min(D,R), clock-adjusted bound r times that gain. Positive unseen seed 259101; negative 259102; divergent correctness adversary 259103. Strongest control: optimized bank-aware scheduler and best compiler-static rematerialization with matched resources. Source, checks and physical PPA are not yet published or verified. No architecture claim.
