// V262 frozen E0 smallest encoding kernel. Not yet simulated/synthesized.
// External one-bit mode sideband must be present in BOTH candidate and controls.
module v262_delta_encoder_proxy(
  input wire [15:0] a0,a1,a2,a3,
  output wire compressible,
  output wire [31:0] packet
);
  wire signed [16:0] d1={1'b0,a1}-{1'b0,a0};
  wire signed [16:0] d2={1'b0,a2}-{1'b0,a0};
  wire signed [16:0] d3={1'b0,a3}-{1'b0,a0};
  assign compressible = (d1>=-17'sd16 && d1<=17'sd15) &&
                        (d2>=-17'sd16 && d2<=17'sd15) &&
                        (d3>=-17'sd16 && d3<=17'sd15);
  // Bit 31 is reserved; compressible is the one-bit mode sideband,
  // provided with identical wiring to both candidate and control.
  // Raw fallback is two 32-bit beats, separately packetized.
  assign packet={1'b0,a0,d1[4:0],d2[4:0],d3[4:0]};
endmodule
