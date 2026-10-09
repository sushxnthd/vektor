// Vektor-052 experimental RF read arbiter. This is NOT a tagged operand collector.
// POLICY 0: clock RR, 1: first-grant RR, 2: completion-first.
module rf_policy_052 #(
  parameter integer W=4, B=2, O=3, PORTS=2, POLICY=2,
  parameter integer BW=(B<2 ? 1 : $clog2(B)),
  parameter integer WW=(W<2 ? 1 : $clog2(W)),
  parameter integer SW=(W*O<2 ? 1 : $clog2(W*O+1))
)(
  input wire clk, rst_n,
  input wire [W*O-1:0] pending_mask, accepted_mask,
  input wire [W*O*BW-1:0] bank_ids,
  input wire [SW-1:0] free_slots,
  output reg [W*O-1:0] grant,
  output reg [SW-1:0] grant_count,
  output reg [WW-1:0] pointer
);
  integer bank_used[0:B-1];
  integer n, first, rank, k, w, o, b, collected;
  always @* begin
    grant=0; grant_count=0; n=0; first=-1;
    for (k=0;k<B;k=k+1) bank_used[k]=0;
    for (rank=O;rank>=0;rank=rank-1) begin
      for (k=0;k<W;k=k+1) begin
        w=pointer+k;
        if (w>=W) w=w-W;
        collected=0;
        for (o=0;o<O;o=o+1)
          if (accepted_mask[w*O+o]) collected=collected+1;
        if (((POLICY==2) && (collected==rank)) ||
            ((POLICY!=2) && (rank==O))) begin
          for (o=0;o<O;o=o+1) begin
            b=bank_ids[(w*O+o)*BW +: BW];
            if (pending_mask[w*O+o] && !accepted_mask[w*O+o] &&
                n<free_slots && b>=0 && b<B && bank_used[b]<PORTS) begin
              grant[w*O+o]=1'b1;
              bank_used[b]=bank_used[b]+1;
              n=n+1;
              if (first<0) first=w;
            end
          end
        end
      end
    end
    grant_count=n;
  end
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) pointer<=0;
    else if (POLICY==0) pointer<=(pointer==W-1) ? 0 : pointer+1'b1;
    else if (first>=0) pointer<=(first==W-1) ? 0 : first+1;
  end
endmodule
