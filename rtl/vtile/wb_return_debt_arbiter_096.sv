// Vektor-096: experimental return arbiter; NOT yet RTL verified.
// Producers must hold valid/data stable until accepted.
module wb_return_debt_arbiter_096 #(
 parameter integer SOURCES=4, TAG_BITS=3, AGE_BITS=16,
 parameter integer GUARD=128, IDX_BITS=$clog2(SOURCES)
)(
 input wire clk,rst_n,
 input wire [SOURCES-1:0] src_valid,src_final,
 input wire [SOURCES*TAG_BITS-1:0] src_tags,
 input wire sink_ready,
 output reg [SOURCES-1:0] src_ready,
 output reg out_valid,out_final,
 output reg [TAG_BITS-1:0] out_tag,
 output reg [IDX_BITS-1:0] out_source
);
 reg [IDX_BITS-1:0] rr;
 reg [AGE_BITS-1:0] age [0:SOURCES-1];
 integer i,k,choice,rot_idx,best_age;
 reg urgent_found,final_found;
 localparam [AGE_BITS-1:0] AGE_MAX={AGE_BITS{1'b1}};
 always @* begin
   choice=-1;best_age=-1;urgent_found=0;final_found=0;rot_idx=0;
   for(k=0;k<SOURCES;k=k+1) begin
     rot_idx=rr+k;
     if(rot_idx>=SOURCES)rot_idx=rot_idx-SOURCES;
     if(src_valid[rot_idx] && age[rot_idx]>=GUARD &&
       (!urgent_found || age[rot_idx]>best_age)) begin
       urgent_found=1;best_age=age[rot_idx];choice=rot_idx;
     end
   end
   if(!urgent_found) begin
     for(k=0;k<SOURCES;k=k+1) begin
       rot_idx=rr+k;
       if(rot_idx>=SOURCES)rot_idx=rot_idx-SOURCES;
       if(src_valid[rot_idx] && src_final[rot_idx] && !final_found) begin
         final_found=1;choice=rot_idx;
       end
     end
     if(!final_found) begin
       for(k=0;k<SOURCES;k=k+1) begin
         rot_idx=rr+k;
         if(rot_idx>=SOURCES)rot_idx=rot_idx-SOURCES;
         if(src_valid[rot_idx] && choice<0)choice=rot_idx;
       end
     end
   end
   src_ready=0;out_valid=(choice>=0);
   out_final=0;out_tag=0;out_source=0;
   if(choice>=0) begin
     out_final=src_final[choice];
     out_tag=src_tags[choice*TAG_BITS +: TAG_BITS];
     out_source=choice;
     if(sink_ready)src_ready[choice]=1;
   end
 end
 always @(posedge clk or negedge rst_n) begin
   if(!rst_n) begin
     rr<=0;
     for(i=0;i<SOURCES;i=i+1)age[i]<=0;
   end else begin
     if(out_valid && sink_ready) begin
       if(out_source==SOURCES-1)rr<=0;
       else rr<=out_source+1'b1;
     end
     for(i=0;i<SOURCES;i=i+1) begin
       if(!src_valid[i] || src_ready[i])age[i]<=0;
       else if(age[i]!=AGE_MAX)age[i]<=age[i]+1'b1;
     end
   end
 end
endmodule
