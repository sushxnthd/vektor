`timescale 1ns/1ps
module tb_replay_fence_072;
reg clk=0; always #5 clk=~clk;
reg rst_n=0,source_valid=0,replay_valid=0,fence_req=0,epoch_release=0;
reg sink_ready=0,sink_drop=0,sink_stall=1;
wire source_ready,replay_ready,producer_valid,producer_ready;
wire [1:0] producer_uid,sink_uid;
wire fence_ack,quiescent,sink_valid;
wire [2:0] source_occ,ack_occ,data_occ;
integer deliveries=0;
replay_source_072 #(.UID_W(2),.DEPTH(4)) producer (
.clk(clk),.rst_n(rst_n),.fence_req(fence_req),.epoch_release(epoch_release),
.source_valid(source_valid),.source_ready(source_ready),.source_uid(2'b00),
.replay_valid(replay_valid),.replay_ready(replay_ready),.replay_uid(2'b00),
.out_valid(producer_valid),.out_ready(producer_ready),.out_uid(producer_uid),
.fence_ack(fence_ack),.occupancy(source_occ));
bounded_fabric_071 #(.UID_W(2),.DEPTH(4)) fabric (
.clk(clk),.rst_n(rst_n),
.data_in_valid(1'b0),.data_in_uid(2'b00),.data_clone(1'b0),
.data_out_ready(1'b1),.data_drop(1'b0),.data_stall(1'b0),
.ack_in_valid(producer_valid),.ack_in_ready(producer_ready),
.ack_in_uid(producer_uid),.ack_clone(1'b1),
.ack_out_valid(sink_valid),.ack_out_ready(sink_ready),
.ack_out_uid(sink_uid),.ack_drop(sink_drop),.ack_stall(sink_stall),
.producer_closed(fence_ack),.external_inflight(1'b0),
.quiescent(quiescent),.data_occupancy(data_occ),.ack_occupancy(ack_occ));
always @(posedge clk) if (rst_n) begin
if(sink_valid && sink_ready) deliveries=deliveries+1;
if(quiescent && (ack_occ!=0 || source_occ!=0 || !fence_ack))
$fatal(1,"incorrect fence");
end
task tick; begin @(posedge clk); #1; end endtask
integer i;
initial begin
tick(); rst_n=1;
source_valid=1; tick(); source_valid=0;
replay_valid=1; tick(); replay_valid=0;
fence_req=1; replay_valid=1; #1;
if(replay_ready || source_ready) $fatal(1,"late admission");
tick(); fence_req=0; replay_valid=0;
repeat(6) tick();
if(!fence_ack || ack_occ!=4 || quiescent) $fatal(1,"early retirement");
sink_drop=1; sink_stall=0;
repeat(4) tick(); sink_drop=0;
if(!quiescent || ack_occ!=0 || deliveries!=0) $fatal(1,"drain");
epoch_release=1; tick(); epoch_release=0;
if(fence_ack || quiescent) $fatal(1,"release");
source_valid=1; tick(); source_valid=0;
fence_req=1; tick(); fence_req=0;
sink_ready=1;
for(i=0;i<12 && !quiescent;i=i+1) tick();
if(!quiescent || deliveries!=2 || ack_occ!=0) $fatal(1,"epoch isolation");
$display("PASS Vektor-072 integrated RTL");
$finish;
end
endmodule
