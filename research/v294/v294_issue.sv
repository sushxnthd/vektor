// V294 single-cycle conflict escape, two ports per RF bank.
// Bitmask occupancy avoids dynamically indexed array updates in synthesis.
module v294_issue #(parameter LOOKAHEAD=1)(
 input wire [3:0] primary_valid,alternate_valid,
 input wire [15:0] p_bank0,p_bank1,a_bank0,a_bank1,
 output reg [3:0] grant,use_alternate
);
 reg [15:0] once,twice;
 reg [3:0] p0,p1,a0,a1,q0,q1,s0,s1;
 reg [3:0] score_p,score_a;
 reg fit_p,fit_a,choose_a;
 integer slot,j;
 always @* begin
   once=0;twice=0;grant=0;use_alternate=0;
   p0=0;p1=0;a0=0;a1=0;q0=0;q1=0;s0=0;s1=0;
   score_p=0;score_a=0;fit_p=0;fit_a=0;choose_a=0;
   for(slot=0;slot<4;slot=slot+1) begin
     p0=p_bank0[slot*4 +:4];p1=p_bank1[slot*4 +:4];
     a0=a_bank0[slot*4 +:4];a1=a_bank1[slot*4 +:4];
     fit_p=primary_valid[slot] && ((p0==p1) ?
       !once[p0] : (!twice[p0] && !twice[p1]));
     fit_a=alternate_valid[slot] && ((a0==a1) ?
       !once[a0] : (!twice[a0] && !twice[a1]));
     score_p=0;score_a=0;
     for(j=0;j<4;j=j+1) begin
       if(j>slot && primary_valid[j]) begin
         q0=p_bank0[j*4 +:4];q1=p_bank1[j*4 +:4];
         if(q0==p0) score_p=score_p+1'b1;
         if(q1==p0) score_p=score_p+1'b1;
         if(q0==p1) score_p=score_p+1'b1;
         if(q1==p1) score_p=score_p+1'b1;
         if(q0==a0) score_a=score_a+1'b1;
         if(q1==a0) score_a=score_a+1'b1;
         if(q0==a1) score_a=score_a+1'b1;
         if(q1==a1) score_a=score_a+1'b1;
       end
     end
     choose_a=fit_a && (!fit_p || (LOOKAHEAD && score_a<score_p));
     if(fit_p || fit_a) begin
       grant[slot]=1'b1;use_alternate[slot]=choose_a;
       s0=choose_a?a0:p0;s1=choose_a?a1:p1;
       if(s0==s1) begin
         once[s0]=1'b1;twice[s0]=1'b1;
       end else begin
         if(once[s0]) twice[s0]=1'b1; else once[s0]=1'b1;
         if(once[s1]) twice[s1]=1'b1; else once[s1]=1'b1;
       end
     end
   end
 end
endmodule
