`timescale 1ns/1ps
module tb_fabric_071;
 reg clk=0; always #5 clk=~clk;
 reg rst_n=0,di=0,dc=0,do_ready=0,do_drop=0,do_stall=0;
 reg ai=0,ac=0,ao_ready=0,ao_drop=0,ao_stall=0,closed=0,external=0;
 reg [1:0] duid=0,auid=0;
 wire dir,dov,air,aov,q;
 wire [1:0] dou,aou;
 wire [2:0] dcount,acount;
 integer d_terminal=0,a_terminal=0,d_deliver=0,a_deliver=0;
 bounded_fabric_071 #(.UID_W(2),.DEPTH(4)) dut(
 .clk(clk),.rst_n(rst_n),.data_in_valid(di),.data_in_ready(dir),
 .data_in_uid(duid),.data_clone(dc),.data_out_valid(dov),
 .data_out_ready(do_ready),.data_out_uid(dou),.data_drop(do_drop),
 .data_stall(do_stall),.ack_in_valid(ai),.ack_in_ready(air),
 .ack_in_uid(auid),.ack_clone(ac),.ack_out_valid(aov),
 .ack_out_ready(ao_ready),.ack_out_uid(aou),.ack_drop(ao_drop),
 .ack_stall(ao_stall),.producer_closed(closed),.external_inflight(external),
 .quiescent(q),.data_occupancy(dcount),.ack_occupancy(acount));
 always @(posedge clk) if(rst_n) begin
   if(dcount!=0 && !do_stall && (do_drop || do_ready)) begin
     d_terminal=d_terminal+1; if(dov && do_ready) d_deliver=d_deliver+1;
   end
   if(acount!=0 && !ao_stall && (ao_drop || ao_ready)) begin
     a_terminal=a_terminal+1; if(aov && ao_ready) a_deliver=a_deliver+1;
   end
 end
 task tick; begin @(posedge clk); #1; end endtask
 initial begin
   tick(); rst_n=1;
   di=1; dc=1; duid=0; tick(); di=0; dc=0;
   if(dcount!=2 || q) $fatal(1,"data clone accounting");
   do_drop=1; tick(); do_drop=0;
   if(dcount!=1 || d_terminal!=1) $fatal(1,"drop must terminate exactly one");
   do_ready=1; tick(); do_ready=0;
   if(dcount!=0 || d_deliver!=1) $fatal(1,"second copy delivery");
   ai=1; ac=1; auid=0; tick(); ai=0; ac=0;
   closed=1; if(q || acount!=2) $fatal(1,"premature fence");
   ao_ready=1; tick(); ao_ready=0;
   if(q || acount!=1) $fatal(1,"first ACK cannot certify drain");
   ao_stall=1; repeat(3) tick();
   if(q || acount!=1) $fatal(1,"stalled ACK copy lost");
   ao_stall=0; ao_drop=1; tick(); ao_drop=0;
   if(!q || a_terminal!=2 || a_deliver!=1) $fatal(1,"quiescence conservation");
   external=1; if(q) $fatal(1,"external packet must block fence");
   external=0; if(!q) $fatal(1,"external fence release");
   $display("PASS Vektor-071 bounded physical-copy accounting");
   $finish;
 end
endmodule
