# V244 retirement / physicality ledger
Evidence class: synthetic software oracle + structural prior-art audit. NOT physical PPA.
Bottleneck: two-way parallel data lookup E=Etag+2Eway; phased E=Etag+(1-m)Eway+Ectrl. Relative saving iff (1+m)Eway>Ectrl; against one-way early-select baseline iff m Eway>Ectrl.
Mechanism: hit-qualified way wordline enable; no data read on miss.
Strongest equal-resource baseline: conventional phased cache; same Boolean function, ports, buffers, wires and possible RTL.
Prediction: high-miss frozen seed 244101 saves activity vs weak parallel, high-hit seed 244102 loses modeled hit-critical throughput. Both tie phased control.
Falsification: 16,384 configurations equal; no incremental PPA mechanism exists against same phased control. Prior art Inoue/Ishihara/Murakami ISLPED 1999 DOI 10.1145/313817.313948 explicitly compares phased cache.
Physicality: RTL prepared but not simulated. Yosys/STA unavailable; max-cap, slew, wire/load, SRAM power not checked. Do not infer energy from toggle count.
Synthetic proxy Etag=0.2,Eway=1,Ectrl=0.08; 20,000 lookups per regime. Positive memory misses=0.85215, reads=2957; negative compute misses=0.05315, reads=18937. Both within frozen 2 pp.
Area/timing: identical Boolean cones allow identical netlists; physical values not measured.
Integrated tile unchanged; V153/V156 FP32 claims electrically disqualified. Retire V244. Next V245 only.
