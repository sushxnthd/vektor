module vektor_rf_exchange_arbiter (
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    input wire [1:0] priority_turn,
    output reg [3:0] grant,
    output reg [3:0] greedy_grant
);
function automatic legal;
 input [3:0] candidate;
 input [15:0] b0,b1;
 integer bank,slot,count;
 begin
  legal=1'b1;
  for(bank=0;bank<16;bank=bank+1) begin
   count=0;
   for(slot=0;slot<4;slot=slot+1)
    if(candidate[slot]) begin
     if(b0[slot*4 +:4]==bank) count=count+1;
     if(b1[slot*4 +:4]==bank) count=count+1;
    end
   if(count>2) legal=1'b0;
  end
 end
endfunction
integer k,i,drop,a,b;
reg [3:0] trial,candidate;
reg found;
always @* begin
 greedy_grant=4'b0;
 for(k=0;k<4;k=k+1) begin
  i=(priority_turn+k)&3;
  trial=greedy_grant | (4'b1 << i);
  if(request_valid[i] && legal(trial,src0_bank_flat,src1_bank_flat))
   greedy_grant=trial;
 end
 grant=greedy_grant;
 found=1'b0;
 candidate=4'b0;
 for(drop=0;drop<4;drop=drop+1)
  for(a=0;a<4;a=a+1)
   for(b=a+1;b<4;b=b+1) begin
    candidate=(greedy_grant & ~(4'b1 << drop)) | (4'b1 << a) | (4'b1 << b);
    if(!found && greedy_grant[drop] && !greedy_grant[a] &&
       !greedy_grant[b] && request_valid[a] && request_valid[b] &&
       legal(candidate,src0_bank_flat,src1_bank_flat)) begin
     grant=candidate;
     found=1'b1;
    end
   end
end
endmodule
