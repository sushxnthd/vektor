# V203 CI and physicality state

- Commit 2200093ae017d33a1e2045f58d455a7bfa153eec introduced candidate arbiter and 20,002-vector RTL test; inherited RTL/simulator CI passed on that SHA.
- Matched baseline RTL preserved at research/v203/rtl/baseline.sv.
- Attempt to add a new matched Nangate45 synthesis/OpenSTA workflow was blocked by repository safety checks. No fresh matched STA or electrical qualification can be claimed.
- Previous V156 infrastructure error (Yosys write_verilog flag) was resolved in V156, but V195 found max-cap violations. V153 cutset is inactive.
- Candidate lacks decoder same-register metadata and operand broadcast; integrated issue_control ties src_alias=0.
- Next: inspect candidate RTL synthesis logs and compare generic cell counts against V202 baseline; then perform one matched mapped timing/electrical attempt or kill this mechanism.

## Verified inherited CI (2026-10-18)

- V203 SHA 8e002c12995ac10b392bd42656f4a9252689774c: simulator PASS (run 39109041758), RTL PASS (run 39109041884). The V203 arbiter testbench executed 20,002 directed/random vectors; existing integrated issue_control tests passed with alias tied low.
- Matched generic Yosys comparison from workflow logs (same inherited rtl.yml): original baseline 1,321 generic cells (run 39108862116); V203 candidate 1,413 generic cells (run 39108999950). Delta +92 (+6.96%). These are logic cell counts, NOT Nangate45 area or timing.
- Matched mapped STA/max-cap/slew remains UNEXECUTED. Physicality gate is OPEN; candidate cannot be selected as a Pareto architecture.
- Reproducible Python model/checker ran locally, but a repository write for those Python sources was blocked by safety checks; CSV and ledgers are on branch. The downloadable local research package preserves executable Python sources.
