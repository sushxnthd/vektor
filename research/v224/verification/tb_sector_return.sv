module tb_sector_return;
reg [127:0] line;
wire [3:0] sm,bm;wire [127:0] sp,bp,sd,bd;wire [2:0] sc,bc;
integer t,k;
v224_sector_encode u_s(line,sm,sp,sc);
v224_line_encode u_b(line,bm,bp,bc);
v224_decode u_sd(sm,sp,sd);
v224_decode u_bd(bm,bp,bd);
initial begin
 for(t=0;t<10000;t=t+1) begin
  for(k=0;k<4;k=k+1) begin
   if((t+k)%5<2) line[k*32 +:32]=0;
   else line[k*32 +:32]=$random;
  end
  #1;
  if(sd!==line||bd!==line) $fatal(1,"lossless fail %0d",t);
  if(sc!==({2'b0,sm[0]}+{2'b0,sm[1]}+{2'b0,sm[2]}+{2'b0,sm[3]})) $fatal(1,"count fail");
  if(bc!==((line==0)?3'd0:3'd4)) $fatal(1,"control count fail");
  if(sc>bc) $fatal(1,"traffic inflated");
 end
 $display("V224 PASS 10000 differential RTL cases");
 $finish;
end
endmodule
