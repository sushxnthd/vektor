// Vektor-058 experimental ready-response queue; not a complete operand collector.
// FIFO compaction and saturating ages avoid wrap-related priority inversions.
module tagged_return_queue_058 #(
  parameter integer N=8,
  parameter integer TAGW=16,
  parameter integer DATAW=16,
  parameter integer REMW=2,
  parameter integer AGEW=3,
  parameter integer AGE_LIMIT=4,
  parameter integer CW=(N>1 ? $clog2(N+1) : 1)
)(
  `include "ports_058.vh"
  reg [TAGW-1:0] q_tag[0:N-1];
  reg [DATAW-1:0] q_data[0:N-1];
  reg [REMW-1:0] q_rem[0:N-1];
  reg [AGEW-1:0] q_age[0:N-1];
  `include "selector_058.vh"
  `include "state_058.vh"
endmodule
