// V295: 32-wave parallel one-hot bank predecode, compared with decode-after-select.
// PREDECODE 0 and 1 use identical scheduler, arbiter, bank ports and state.
module v295_issue_core #(parameter PREDECODE=1)(
 input wire clk,rst_n,
 input wire [31:0] wave_valid,wave_ready,
 input wire [127:0] src0_bank_by_wave,src1_bank_by_wave,
 output wire [3:0] issue_valid,
 output wire [4:0] issue_wave0,issue_wave1,issue_wave2,issue_wave3
);
 wire [3:0] sv;
 wire [4:0] sw0,sw1,sw2,sw3;
 wire [3:0] accept;
 vektor_steal_warp_scheduler scheduler(
  .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
  .issue_accept(accept),.issue_valid(sv),
  .issue_wave0(sw0),.issue_wave1(sw1),.issue_wave2(sw2),.issue_wave3(sw3)
 );
 function [3:0] selected_bank;
  input [127:0] banks;
  input [4:0] wave_id;
  reg [127:0] shifted;
  begin shifted=banks >> (wave_id*4); selected_bank=shifted[3:0]; end
 endfunction
 wire [15:0] hot0 [0:31],hot1 [0:31];
 genvar w,s;
 generate for(w=0;w<32;w=w+1) begin: decode_all
  assign hot0[w]=16'h0001 << src0_bank_by_wave[w*4 +: 4];
  assign hot1[w]=16'h0001 << src1_bank_by_wave[w*4 +: 4];
 end endgenerate
 wire [15:0] m0 [0:3],m1 [0:3];
 generate for(s=0;s<4;s=s+1) begin: selected
  wire [4:0] id;
  if(s==0) assign id=sw0;
  else if(s==1) assign id=sw1;
  else if(s==2) assign id=sw2;
  else assign id=sw3;
  if(PREDECODE) begin: parallel
   reg [15:0] x,y;
   integer j;
   always @* begin
    x=0;y=0;
    for(j=0;j<32;j=j+1)
     if(id==j) begin x=x|hot0[j];y=y|hot1[j];end
   end
   assign m0[s]=x;
   assign m1[s]=y;
  end else begin: serial
   assign m0[s]=16'h0001 << selected_bank(src0_bank_by_wave,id);
   assign m1[s]=16'h0001 << selected_bank(src1_bank_by_wave,id);
  end
 end endgenerate
 reg [3:0] grant;
 reg [15:0] once,twice,a,b;
 reg fit;
 integer slot;
 always @* begin
  grant=0;once=0;twice=0;a=0;b=0;fit=0;
  for(slot=0;slot<4;slot=slot+1) begin
   a=m0[slot];b=m1[slot];fit=0;
   if(sv[slot]) begin
    if(|(a&b)) fit=((once&a)==0);
    else fit=((twice&a)==0)&&((twice&b)==0);
    if(fit) begin
     grant[slot]=1;
     if(|(a&b)) begin once=once|a;twice=twice|a;end
     else begin twice=twice|(once&(a|b));once=once|a|b;end
    end
   end
  end
 end
 assign accept=sv&grant;
 assign issue_valid=accept;
 assign issue_wave0=sw0;
 assign issue_wave1=sw1;
 assign issue_wave2=sw2;
 assign issue_wave3=sw3;
endmodule
