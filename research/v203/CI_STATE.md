# V203 CI and physicality state

- Commit 2200093ae017d33a1e2045f58d455a7bfa153eec introduced candidate arbiter and 20,002-vector RTL test; inherited RTL/simulator CI passed on that SHA.
- Matched baseline RTL preserved at research/v203/rtl/baseline.sv.
- Attempt to add a new matched Nangate45 synthesis/OpenSTA workflow was blocked by repository safety checks. No fresh matched STA or electrical qualification can be claimed.
- Previous V156 infrastructure error (Yosys write_verilog flag) was resolved in V156, but V195 found max-cap violations. V153 cutset is inactive.
- Candidate lacks decoder same-register metadata and operand broadcast; integrated issue_control ties src_alias=0.
- Next: inspect candidate RTL synthesis logs and compare generic cell counts against V202 baseline; then perform one matched mapped timing/electrical attempt or kill this mechanism.
