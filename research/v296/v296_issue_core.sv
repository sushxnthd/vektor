// V296: pairwise equality graph for two-port RF-bank admission.
// Same scheduler, RF ports, issue slots, wave state as original V-Tile.
module v296_issue_core(
 input wire clk,rst_n,
 input wire [31:0] wave_valid,wave_ready,
 input wire [127:0] src0_bank_by_wave,src1_bank_by_wave,
 output wire [3:0] issue_valid,
 output wire [4:0] issue_wave0,issue_wave1,issue_wave2,issue_wave3
);
 wire [3:0] sv,grant,accept;
 wire [4:0] sw0,sw1,sw2,sw3;
 wire [15:0] bank0,bank1;
 function [3:0] selected_bank;
  input [127:0] banks;
  input [4:0] wave_id;
  reg [127:0] shifted;
  begin shifted=banks >> (wave_id*4);selected_bank=shifted[3:0];end
 endfunction
 vektor_steal_warp_scheduler scheduler(
  .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
  .issue_accept(accept),.issue_valid(sv),
  .issue_wave0(sw0),.issue_wave1(sw1),.issue_wave2(sw2),.issue_wave3(sw3)
 );
 assign bank0[3:0]=selected_bank(src0_bank_by_wave,sw0);
 assign bank0[7:4]=selected_bank(src0_bank_by_wave,sw1);
 assign bank0[11:8]=selected_bank(src0_bank_by_wave,sw2);
 assign bank0[15:12]=selected_bank(src0_bank_by_wave,sw3);
 assign bank1[3:0]=selected_bank(src1_bank_by_wave,sw0);
 assign bank1[7:4]=selected_bank(src1_bank_by_wave,sw1);
 assign bank1[11:8]=selected_bank(src1_bank_by_wave,sw2);
 assign bank1[15:12]=selected_bank(src1_bank_by_wave,sw3);
 v296_pairwise_arbiter arb(.request_valid(sv),.bank0(bank0),.bank1(bank1),.grant(grant));
 assign accept=sv&grant;
 assign issue_valid=accept;
 assign issue_wave0=sw0;
 assign issue_wave1=sw1;
 assign issue_wave2=sw2;
 assign issue_wave3=sw3;
endmodule

module v296_pairwise_arbiter(
 input wire [3:0] request_valid,
 input wire [15:0] bank0,bank1,
 output reg [3:0] grant
);
 reg [3:0] a,b,pa,pb;
 reg [2:0] hits_a,hits_b;
 integer i,j;
 always @* begin
  grant=0;a=0;b=0;pa=0;pb=0;hits_a=0;hits_b=0;
  for(i=0;i<4;i=i+1) begin
   a=bank0[i*4 +:4];b=bank1[i*4 +:4];
   hits_a=0;hits_b=0;
   for(j=0;j<4;j=j+1) begin
    if(j<i && grant[j]) begin
     pa=bank0[j*4 +:4];pb=bank1[j*4 +:4];
     if(pa==a) hits_a=hits_a+3'd1;
     if(pb==a) hits_a=hits_a+3'd1;
     if(pa==b) hits_b=hits_b+3'd1;
     if(pb==b) hits_b=hits_b+3'd1;
    end
   end
   if(request_valid[i]) begin
    if(a==b) begin
     if(hits_a==0) grant[i]=1'b1;
    end else if(hits_a<2 && hits_b<2) grant[i]=1'b1;
   end
  end
 end
endmodule
