// V263 exploratory RTL only: NOT simulated, synthesized, or electrically qualified.
module v263_bank_arbiter(
 input logic valid0,valid1,last0,last1,starved0,starved1,
 input logic [7:0] age0,age1,
 output logic grant0,grant1
);
 logic prefer0;
 always_comb begin
  if (starved0 != starved1) prefer0 = starved0;
  else if (last0 != last1) prefer0 = last0;
  else prefer0 = age0 >= age1;
  grant0 = valid0 && (!valid1 || prefer0);
  grant1 = valid1 && (!valid0 || !prefer0);
 end
endmodule
