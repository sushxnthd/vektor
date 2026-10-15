# V156 timing validity boundary

The OpenSTA comparison remains incomplete. The buffered control report parsed without an OpenSTA error and reported -2.93 ns worst slack against a 10 ns constraint. The cutset report printed an `Error:` while reading the generated netlist, so its apparent +1.65 ns slack is invalid evidence and must not be compared to the control. A subsequent attempt failed during synthesis because Yosys 0.9 does not recognize `write_verilog -simple-lhs`.

The next experiment is to normalize the mapped netlist with Yosys `splitnets`, rerun the exact matched OpenSTA control and cutset, and reject either log containing any parser errors. These are infrastructure failures, not scientific falsification. Preserve Actions runs 38795100007 and 38795918466. No timing or area-delay advantage is established, and no physical PPA or scientific novelty is claimed.
