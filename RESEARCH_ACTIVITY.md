# Research Activity

Updated: 2026-11-08 (UTC)

- Active research branch: `research/v317-sass-provenance-gate`
- Active draft PR: #34
- Latest durable research commit: `47ac5a8ec61fa9e5cdaf4ff4ffb323eb07c8a48e`
- Evidence: committed independent bank-skew capacity audit with exhaustive two-bank allocation oracle. For 100 cycles, four 1-port banks and four shared return ports, demand (160,0,0,0) yields a bank-aware optimistic ceiling of 100 completions, while pooling bank capacity falsely permits 160. The equivalent local model passed 2,304 exhaustive cases; committed script was fetched back from GitHub, but not executed verbatim. This is a conservation falsification, not RTL/STA, electrical signoff, measured GPU IPC, or a surviving positive architecture mechanism.
- Earlier V317 physical failures and V296 throughput no-go remain binding. Experimental evidence stays on the research branch; this ledger is not validation or release approval.
