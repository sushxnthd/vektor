// V289: critical-first within each single-read-port bank, age=index tie-break.
// Four pending requests, two banks, at most one grant per bank.
// This is a combinational arbiter only; not a complete RF or GPU.
module v289_critical_bank_admit(
 input wire [3:0] valid,
 input wire [3:0] bank,
 input wire [3:0] critical,
 output reg [3:0] grant
);
 integer b,i,chosen;
 always @* begin
   grant=4'b0000;
   for(b=0;b<2;b=b+1) begin
     chosen=-1;
     for(i=0;i<4;i=i+1)
       if(valid[i] && bank[i] == b[0]) begin
         if(chosen == -1) chosen=i;
         else if(critical[i] && !critical[chosen]) chosen=i;
       end
     if(chosen >= 0) grant[chosen]=1'b1;
   end
 end
endmodule

// Equal-port, equal-buffer age-first baseline, one grant per occupied bank.
module v289_age_bank_admit(
 input wire [3:0] valid,
 input wire [3:0] bank,
 input wire [3:0] critical,
 output reg [3:0] grant
);
 integer b,i,chosen;
 always @* begin
   grant=4'b0000;
   for(b=0;b<2;b=b+1) begin
     chosen=-1;
     for(i=0;i<4;i=i+1)
       if(valid[i] && bank[i] == b[0] && chosen == -1) chosen=i;
     if(chosen >= 0) grant[chosen]=1'b1;
   end
 end
endmodule
