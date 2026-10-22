`timescale 1ns/1ps
module tb_v285_matched;
 reg [3:0] valid;
 reg [15:0] a,b;
 wire [3:0] gp,gf;
 integer it,i,j,bank,step,idx,best;
 integer count[0:15],score[0:3],used[0:15],usedfixed[0:15];
 reg [3:0] aa[0:3],bb[0:3];
 reg [3:0] seen,expected,expectedfixed;
 v285_pressure_priority_arbiter p(valid,a,b,gp);
 v285_fixed_priority_arbiter f(valid,a,b,gf);
 initial begin
  for(it=0;it<10000;it=it+1)begin
   valid=$random;a=$random;b=$random;
   for(i=0;i<4;i=i+1)begin aa[i]=a[4*i +:4];bb[i]=b[4*i +:4];end
   for(bank=0;bank<16;bank=bank+1)begin count[bank]=0;used[bank]=0;usedfixed[bank]=0;end
   for(i=0;i<4;i=i+1)if(valid[i])begin count[aa[i]]=count[aa[i]]+1;count[bb[i]]=count[bb[i]]+1;end
   for(i=0;i<4;i=i+1)score[i]=count[aa[i]]+count[bb[i]];
   expected=0;seen=0;expectedfixed=0;
   for(step=0;step<4;step=step+1)begin
    idx=-1;best=99;
    for(j=0;j<4;j=j+1)if(valid[j] && !seen[j] && score[j]<best)begin best=score[j];idx=j;end
    if(idx>=0)begin
     seen[idx]=1'b1;
     if(used[aa[idx]]<2 && used[bb[idx]]+((aa[idx]==bb[idx])?1:0)<2)begin
      expected[idx]=1'b1;used[aa[idx]]=used[aa[idx]]+1;used[bb[idx]]=used[bb[idx]]+1;
     end
    end
   end
   for(i=0;i<4;i=i+1)if(valid[i])begin
    if(usedfixed[aa[i]]<2 && usedfixed[bb[i]]+((aa[i]==bb[i])?1:0)<2)begin
     expectedfixed[i]=1'b1;usedfixed[aa[i]]=usedfixed[aa[i]]+1;usedfixed[bb[i]]=usedfixed[bb[i]]+1;
    end
   end
   #1;
   if(gp!==expected)$fatal(1,"pressure mismatch case %0d valid %b got %b expected %b",it,valid,gp,expected);
   if(gf!==expectedfixed)$fatal(1,"fixed mismatch case %0d valid %b got %b expected %b",it,valid,gf,expectedfixed);
  end
  $display("PASS 10000 randomized matched oracle cases");
  $finish;
 end
endmodule
