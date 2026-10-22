// V274 retired reference. One RF read port; speculative request suppressed
// when the single collector slot or its in-flight fill is occupied.
// External scoreboard guarantees future_eligible, versioned tags and no
// flush; this module does not implement the RF memory or full response queue.
module v274_one_entry_fixed #(parameter DW=32, TW=12)(
  input wire clk, rst,
  input wire future_valid, future_eligible,
  input wire [TW-1:0] future_tag,
  input wire demand_valid,
  input wire [TW-1:0] demand_tag,
  input wire rf_resp_valid,
  input wire [TW-1:0] rf_resp_tag,
  input wire [DW-1:0] rf_resp_data,
  output wire demand_hit,
  output wire [DW-1:0] bypass_data,
  output wire demand_rf_read,
  output wire prefetch_rf_read,
  output wire [TW-1:0] rf_req_tag
);
  reg slot_valid, prefetch_pending;
  reg [TW-1:0] slot_tag, pending_tag;
  reg [DW-1:0] slot_data;
  assign demand_hit = demand_valid && slot_valid && (slot_tag == demand_tag);
  assign bypass_data = slot_data;
  assign demand_rf_read = demand_valid && !demand_hit;
  assign prefetch_rf_read = !demand_valid && !slot_valid &&
      !prefetch_pending && future_valid && future_eligible;
  assign rf_req_tag = demand_rf_read ? demand_tag : future_tag;
  always @(posedge clk) begin
    if (rst) begin
      slot_valid <= 1'b0;
      slot_tag <= {TW{1'b0}};
      slot_data <= {DW{1'b0}};
      prefetch_pending <= 1'b0;
      pending_tag <= {TW{1'b0}};
    end else begin
      if (demand_hit) slot_valid <= 1'b0;
      if (prefetch_rf_read) begin
        prefetch_pending <= 1'b1;
        pending_tag <= future_tag;
      end
      if (rf_resp_valid) begin
        slot_valid <= 1'b1;
        slot_tag <= rf_resp_tag;
        slot_data <= rf_resp_data;
        if (prefetch_pending && pending_tag == rf_resp_tag)
          prefetch_pending <= 1'b0;
      end
    end
  end
endmodule
