// V294 experimental four-slot bank-conflict escape.
// LOOKAHEAD=0: strongest simple two-choice primary-first fallback control.
// LOOKAHEAD=1: score later primary-bank pressure before selecting a candidate.
// Equal RF port counts and candidate metadata; timing/area MUST be measured.
module v294_issue #(
  parameter LOOKAHEAD = 1
)(
  input wire [3:0] primary_valid,
  input wire [3:0] alternate_valid,
  input wire [15:0] p_bank0, p_bank1,
  input wire [15:0] a_bank0, a_bank1,
  output reg [3:0] grant,
  output reg [3:0] use_alternate
);
  reg [1:0] used [0:15];
  reg [3:0] p0,p1,a0,a1,q0,q1,selected0,selected1;
  reg [3:0] pressure_p,pressure_a;
  reg fit_p,fit_a,select_a,accept;
  integer slot,j,k;
  always @* begin
    grant=4'b0;
    use_alternate=4'b0;
    p0=0;p1=0;a0=0;a1=0;q0=0;q1=0;
    selected0=0;selected1=0;
    pressure_p=0;pressure_a=0;
    fit_p=0;fit_a=0;select_a=0;accept=0;
    for(k=0;k<16;k=k+1) used[k]=2'd0;
    for(slot=0;slot<4;slot=slot+1) begin
      p0=p_bank0[slot*4 +: 4];
      p1=p_bank1[slot*4 +: 4];
      a0=a_bank0[slot*4 +: 4];
      a1=a_bank1[slot*4 +: 4];
      fit_p=primary_valid[slot] &&
        ((p0==p1) ? (used[p0]==0) : ((used[p0]<2)&&(used[p1]<2)));
      fit_a=alternate_valid[slot] &&
        ((a0==a1) ? (used[a0]==0) : ((used[a0]<2)&&(used[a1]<2)));
      pressure_p=0;pressure_a=0;
      for(j=slot+1;j<4;j=j+1) begin
        if(primary_valid[j]) begin
          q0=p_bank0[j*4 +: 4];
          q1=p_bank1[j*4 +: 4];
          if(q0==p0) pressure_p=pressure_p+1'b1;
          if(q1==p0) pressure_p=pressure_p+1'b1;
          if(q0==p1) pressure_p=pressure_p+1'b1;
          if(q1==p1) pressure_p=pressure_p+1'b1;
          if(q0==a0) pressure_a=pressure_a+1'b1;
          if(q1==a0) pressure_a=pressure_a+1'b1;
          if(q0==a1) pressure_a=pressure_a+1'b1;
          if(q1==a1) pressure_a=pressure_a+1'b1;
        end
      end
      select_a=fit_a && (!fit_p || (LOOKAHEAD && pressure_a<pressure_p));
      accept=fit_p || fit_a;
      if(accept) begin
        grant[slot]=1'b1;
        use_alternate[slot]=select_a;
        selected0=select_a ? a0 : p0;
        selected1=select_a ? a1 : p1;
        used[selected0]=used[selected0]+2'd1;
        used[selected1]=used[selected1]+2'd1;
      end
    end
  end
endmodule
