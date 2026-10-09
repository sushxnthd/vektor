// Vektor-057 experimental response selector.
// POLICY 0 FIFO; 1 near-completion; 2 max-age guard; 3 first-urgent guard.
// POLICY 3 is equivalent to 2 only when valid entries are FIFO arrival ordered
// with non-increasing ages; queue and age tracking are external.
module rf_return_select_057 #(
  parameter integer N=8, REMW=2, AGEW=6, AGE_LIMIT=4, POLICY=2,
  parameter integer IW=(N>1 ? $clog2(N) : 1)
)(
  input wire [N-1:0] valid,
  input wire [N*REMW-1:0] remaining,
  input wire [N*AGEW-1:0] age,
  output reg grant_valid,
  output reg [N-1:0] grant_oh,
  output reg [IW-1:0] grant_idx
);
integer i,best;
reg [REMW-1:0] r,best_r;
reg [AGEW-1:0] a,best_a;
reg urgent;
always @* begin
  best=-1;best_r={REMW{1'b1}};best_a={AGEW{1'b0}};
  urgent=1'b0;r=0;a=0;
  if (POLICY==0) begin
    for (i=0;i<N;i=i+1)
      if (valid[i] && best<0) best=i;
  end else begin
    if (POLICY==2 || POLICY==3) begin
      for (i=0;i<N;i=i+1) begin
        a=age[i*AGEW +: AGEW];
        if (valid[i] && a>=AGE_LIMIT &&
            (!urgent || (POLICY==2 && a>best_a))) begin
          urgent=1'b1;best=i;best_a=a;
        end
      end
    end
    if (!urgent) begin
      best=-1;
      for (i=0;i<N;i=i+1) begin
        r=remaining[i*REMW +: REMW];
        if (valid[i] && (best<0 || r<best_r)) begin
          best=i;best_r=r;
        end
      end
    end
  end
  grant_valid=(best>=0);
  grant_oh={N{1'b0}};grant_idx={IW{1'b0}};
  if (best>=0) begin grant_oh[best]=1'b1;grant_idx=best;end
end
endmodule
