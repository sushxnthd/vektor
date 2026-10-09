  input wire clk, input wire rst_n,
  input wire push_valid, output wire push_ready,
  input wire [TAGW-1:0] push_tag,
  input wire [DATAW-1:0] push_data,
  input wire [REMW-1:0] push_remaining,
  output reg pop_valid, input wire pop_ready,
  output reg [TAGW-1:0] pop_tag,
  output reg [DATAW-1:0] pop_data,
  output reg [REMW-1:0] pop_remaining,
  output reg [AGEW-1:0] pop_age,
  output reg pop_urgent,
  output reg [CW-1:0] count
);
