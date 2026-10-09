// Vektor-065 per-slot quiescence tracker (experimental, synthesizable).
// CONTRACT: copy_launch counts *every* physical replica at the last possible
// replication point; copy_terminal fires once per copy on delivery/drop;
// delivered is asserted only with a terminal delivery; after close no new
// copies may appear; ACK path must be reliable and non-replaying.
// Reset requires external fabric quiescence. This block does not enforce it.
module quiescence_tracker_065 #(
  parameter integer ID_W = 16,
  parameter integer COUNT_W = 8
)(
  input  wire clk,
  input  wire rst_n,
  input  wire alloc_valid,
  output wire alloc_ready,
  input  wire [ID_W-1:0] alloc_id,
  input  wire copy_launch,
  input  wire copy_terminal,
  input  wire close_tx,
  input  wire delivered,
  output wire ack_valid,
  input  wire ack_ready,
  output wire [ID_W-1:0] ack_id,
  output reg  fault
);
  reg active;
  reg closed;
  reg delivered_seen;
  reg [COUNT_W-1:0] outstanding;
  reg [ID_W-1:0] id_reg;
  assign alloc_ready = !active;
  assign ack_valid = active && closed && delivered_seen &&
                     (outstanding == {COUNT_W{1'b0}}) && !fault;
  assign ack_id = id_reg;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      active <= 1'b0;
      closed <= 1'b0;
      delivered_seen <= 1'b0;
      outstanding <= {COUNT_W{1'b0}};
      id_reg <= {ID_W{1'b0}};
      fault <= 1'b0;
    end else if (alloc_valid && alloc_ready) begin
      active <= 1'b1;
      closed <= 1'b0;
      delivered_seen <= 1'b0;
      outstanding <= {COUNT_W{1'b0}};
      id_reg <= alloc_id;
      fault <= 1'b0;
    end else if (active) begin
      if ((copy_launch && closed) ||
          (copy_terminal && !copy_launch && outstanding == 0) ||
          (copy_launch && !copy_terminal && (&outstanding)) ||
          (delivered && !copy_terminal))
        fault <= 1'b1;
      if (copy_launch && !copy_terminal && !(&outstanding))
        outstanding <= outstanding + 1'b1;
      if (copy_terminal && !copy_launch && outstanding != 0)
        outstanding <= outstanding - 1'b1;
      if (close_tx)
        closed <= 1'b1;
      if (delivered)
        delivered_seen <= 1'b1;
      if (ack_valid && ack_ready)
        active <= 1'b0;
    end
  end
endmodule
