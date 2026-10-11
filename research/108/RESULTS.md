# V108 verified host-model results

SGEMM two-warp K=8 control: warp/strict/packed sector requests 88/72/72; L1 read misses 20/20/20; wave counts 34/72/34; synthetic service proxy 202/352/322 with migration penalty 4.

Discovery/holdout/surprise configurations: 96/48/20. Strict locality saved sectors yet lost on proxy in 74/164; packed locality in 62/164. Independent C++ replay: 36 traces x 3 policies, all matched. Six Python tests passed. No GPU timing, RTL or PPA evidence.
