// Vektor-099: cancel-wins FINAL consumer; V094 kept as negative control.
// Exactly one FINAL per transaction and cold-reset external quiescence required.
// cancel_mask refers to pre-edge tag incarnation. No duplicate FINAL protection.
module wb_final_consumer_099 #(
  parameter integer TAG_BITS = 3,
  parameter integer N = (1 << TAG_BITS)
)(
  input wire clk,
  input wire cold_rst_n,
  input wire soft_reset,
  input wire flush_ack,
  input wire offer,
  input wire [N-1:0] cancel_mask,
  input wire cb_valid,
  input wire cb_final,
  input wire [TAG_BITS-1:0] cb_tag,
  output reg grant,
  output reg [TAG_BITS-1:0] grant_tag,
  output reg complete,
  output reg stale_drop,
  output reg nonfinal_ignored,
  output reg tag_stall,
  output reg ready,
  output reg [N-1:0] pending_mask,
  output reg [N-1:0] live_mask
);
  reg [TAG_BITS-1:0] rr;
  reg [N-1:0] pending_next, live_next;
  reg choice_valid;
  reg [TAG_BITS-1:0] choice, candidate;
  reg cb_live_match;
  integer k;
  always @* begin
    pending_next = pending_mask;
    live_next = live_mask;
    cb_live_match = 1'b0;
    if (cb_valid && cb_final) begin
      // V099 policy difference: same-cycle cancel overrides completion.
      cb_live_match = pending_mask[cb_tag] && live_mask[cb_tag] && !cancel_mask[cb_tag];
      pending_next[cb_tag] = 1'b0;
      live_next[cb_tag] = 1'b0;
    end
    if (soft_reset) live_next = {N{1'b0}};
    else live_next = live_next & ~cancel_mask;
    choice_valid = 1'b0;
    choice = rr;
    candidate = rr;
    for (k=0; k<N; k=k+1) begin
      candidate = rr + k;
      if (!choice_valid && !pending_next[candidate]) begin
        choice_valid = 1'b1;
        choice = candidate;
      end
    end
    if (ready && !soft_reset && offer && choice_valid) begin
      pending_next[choice] = 1'b1;
      live_next[choice] = 1'b1;
    end
  end
  always @(posedge clk or negedge cold_rst_n) begin
    if (!cold_rst_n) begin
      rr <= 0;
      ready <= 0;
      pending_mask <= 0;
      live_mask <= 0;
      grant <= 0;
      grant_tag <= 0;
      complete <= 0;
      stale_drop <= 0;
      nonfinal_ignored <= 0;
      tag_stall <= 0;
    end else begin
      if (flush_ack) ready <= 1'b1;
      pending_mask <= pending_next;
      live_mask <= live_next;
      grant <= ready && !soft_reset && offer && choice_valid;
      if (ready && !soft_reset && offer && choice_valid) begin
        grant_tag <= choice;
        rr <= choice + 1'b1;
      end
      complete <= cb_valid && cb_final && cb_live_match && !soft_reset;
      stale_drop <= cb_valid && cb_final && !(cb_live_match && !soft_reset);
      nonfinal_ignored <= cb_valid && !cb_final;
      tag_stall <= ready && !soft_reset && offer && !choice_valid;
    end
  end
endmodule
