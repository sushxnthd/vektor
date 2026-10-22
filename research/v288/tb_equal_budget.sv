module tb_equal_budget;
 parameter AW=4, W=32;
 reg [3:0] req_valid;
 reg [4*AW-1:0] req_addr;
 reg bypass_valid;
 reg [AW-1:0] bypass_addr;
 reg [W-1:0] bypass_data;
 wire [3:0] g0,f0,g1,f1;
 wire [4*W-1:0] d0,d1;
 wire [1:0] r0,r1;
 integer code,mask,tag,v,k,n,seed,tests;
 v288_bank_bypass #(.AW(AW),.W(W)) dut(req_valid,req_addr,bypass_valid,bypass_addr,bypass_data,g0,f0,d0,r0);
 v288_operand_cache_control #(.AW(AW),.W(W)) ref_cache(req_valid,req_addr,bypass_valid,bypass_addr,bypass_data,g1,f1,d1,r1);
 task check;
 begin
   #1;
   if ({g0,f0,d0,r0} !== {g1,f1,d1,r1}) begin
     $display("FAIL mask=%h addr=%h bv=%b ba=%h",req_valid,req_addr,bypass_valid,bypass_addr);
     $fatal(1,"V288 unequal control");
   end
   tests=tests+1;
 end
 endtask
 initial begin
   tests=0;
   bypass_data=32'hdeadcafe;
   for(code=0;code<256;code=code+1) begin
     for(k=0;k<4;k=k+1) req_addr[k*AW+:AW]=(code >> (2*k)) & 3;
     for(mask=0;mask<16;mask=mask+1) begin
       req_valid=mask;
       for(v=0;v<2;v=v+1) begin
         bypass_valid=v;
         for(tag=0;tag<4;tag=tag+1) begin
           bypass_addr=tag;
           check();
         end
       end
     end
   end
   seed=28838;
   for(n=0;n<50000;n=n+1) begin
     req_valid=$random(seed);
     req_addr=$random(seed);
     bypass_valid=$random(seed);
     bypass_addr=$random(seed);
     bypass_data=$random(seed);
     check();
   end
   $display("PASS matched V288 vs conventional cache: %0d cases",tests);
   $finish;
 end
endmodule
