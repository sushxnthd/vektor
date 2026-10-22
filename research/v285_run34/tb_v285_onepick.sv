`timescale 1ns/1ps
module tb_v285_onepick;
 reg [3:0] valid;
 reg [15:0] a,b;
 wire [3:0] grant;
 integer it,i,j,k,first,best,score[0:3],count[0:15],used[0:15],idx;
 reg [3:0] aa[0:3],bb[0:3],expected;
 v285_onepick_priority_arbiter dut(valid,a,b,grant);
 initial begin
  for(it=0;it<10000;it=it+1)begin
   valid=$random;a=$random;b=$random;
   for(i=0;i<4;i=i+1)begin aa[i]=a[4*i +:4];bb[i]=b[4*i +:4];end
   for(k=0;k<16;k=k+1)begin count[k]=0;used[k]=0;end
   for(i=0;i<4;i=i+1)if(valid[i])begin count[aa[i]]=count[aa[i]]+1;count[bb[i]]=count[bb[i]]+1;end
   first=-1;best=99;
   for(i=0;i<4;i=i+1)begin
    score[i]=count[aa[i]]+count[bb[i]];
    if(valid[i] && score[i]<best)begin best=score[i];first=i;end
   end
   expected=0;
   for(k=0;k<5;k=k+1)begin
    idx=(k==0)?first:(k-1);
    if(idx>=0 && idx<4 && valid[idx] && (k==0 || idx!=first))begin
     if(used[aa[idx]]<2 && used[bb[idx]]+((aa[idx]==bb[idx])?1:0)<2)begin
      expected[idx]=1'b1;
      used[aa[idx]]=used[aa[idx]]+1;used[bb[idx]]=used[bb[idx]]+1;
     end
    end
   end
   #1;
   if(grant!==expected)$fatal(1,"onepick mismatch case=%0d valid=%b got=%b expected=%b",it,valid,grant,expected);
  end
  $display("PASS onepick 10000 independent oracle cases");
  $finish;
 end
endmodule
