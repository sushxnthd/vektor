module tb_v294;
reg [3:0] pv=4'b1111,av=4'b0001;
reg [15:0] p0=16'h8000,p1=16'h9111,a0=16'h0004,a1=16'h0005;
wire [3:0] g0,g1,u0,u1;
v294_issue #(.LOOKAHEAD(0)) control(pv,av,p0,p1,a0,a1,g0,u0);
v294_issue #(.LOOKAHEAD(1)) candidate(pv,av,p0,p1,a0,a1,g1,u1);
initial begin
 #1;
 if(g0!==4'b1011 || g1!==4'b1111 || u1[0]!==1'b1)
   $fatal(1,"positive holdout failed control=%b candidate=%b alt=%b",g0,g1,u1);
 pv=4'b1111; av=4'b0000;
 p0=16'h6420; p1=16'h7531;
 #1;
 if(g0!==4'b1111 || g1!==4'b1111 || u1!==4'b0000)
   $fatal(1,"no-win holdout failed");
 $display("PASS V294 frozen positive 4/3 and no-win 4/4 directed RTL cases");
 $finish;
end
endmodule
