# V221 pre-registered MSHR boundary

Frozen before holdout execution on 2026-10-19. Only active mechanism: 16-entry MSHR lookup partitioned into four banks of four entries by tag[1:0]. Same storage, one lookup port, and response bandwidth as fully associative CAM.

Law: 16 comparator lanes become 4; for n uniform live tags, P(query bank full)=sum from j=4 to n of binom(n,j)(1/4)^j(3/4)^(n-j). For n=4 P=0.00390625; for n=12 P=0.351221.

Holdout 22117: uniform hash, latency 4, 20,000 requests; predict within 2% of fully associative throughput (positive low occupancy). Holdout 22129: 90% bank-zero hash, latency 12; predict >=10% throughput loss (negative). Holdout 22131: uniform hash, latency 12; predict nonzero loss. Compute-only: zero effect.

Physical positive claim requires >10% mapped area-delay and switching improvement, no >2% throughput loss on positive regime, clean max-cap/slew and realistic load/wire sensitivity. Comparison-count reduction is not an energy measurement. Kill if predecoded fully associative control matches candidate or if electrical checks fail. V153/V156 FP32 is retired as unqualified.

Prior art: banked associative tables and hierarchical GPU MSHRs are established; novelty not claimed.
