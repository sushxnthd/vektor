`timescale 1ns/1ps
module tb_tagged_queue_058;
reg clk=0,rst=1,in_valid=0,out_ready=0;
reg [7:0] in_tag=0;
reg [15:0] in_data=0;
reg [1:0] in_remaining=0;
wire in_ready,out_valid;
wire [7:0] out_tag;
wire [15:0] out_data;
wire [2:0] occupancy;
rf_tagged_ready_queue_058 #(.N(4),.TAGW(8),.DATAW(16),.REMW(2),.AGEW(4),.AGE_LIMIT(3)) dut (
.clk(clk),.rst(rst),.in_valid(in_valid),.in_ready(in_ready),
.in_tag(in_tag),.in_data(in_data),.in_remaining(in_remaining),
.out_valid(out_valid),.out_ready(out_ready),.out_tag(out_tag),
.out_data(out_data),.occupancy(occupancy));
integer f,rc,iv,it,id,ir,ordy,ei,ev,et,ed,ec,n=0;
initial begin
 f=$fopen("research/058/results/vectors_058.txt","r");
 if(f==0)$fatal(1,"missing vectors");
 #2;clk=1;#2;clk=0;rst=0;
 while(!$feof(f))begin
  rc=$fscanf(f,"%d %d %d %d %d %d %d %d %d %d\n",iv,it,id,ir,ordy,ei,ev,et,ed,ec);
  if(rc==10&&iv==-1)begin
   rst=1;in_valid=0;out_ready=0;#2;clk=1;#2;clk=0;rst=0;
  end else if(rc==10)begin
   in_valid=iv;in_tag=it;in_data=id;in_remaining=ir;out_ready=ordy;
   #2;
   if(in_ready!==(ei!=0)||out_valid!==(ev!=0)||out_tag!==et||out_data!==ed||occupancy!==ec)
    $fatal(1,"RTL differential mismatch cycle=%0d",n);
   clk=1;#2;clk=0;#2;n=n+1;
  end
 end
 if(n!=10080)$fatal(1,"expected 10080 cycles; got %0d",n);
 $display("PASS RTL differential cycles=%0d",n);
 $fclose(f);$finish;
end
endmodule
