// V262 decoder combinational proxy, no clock, no physical memory hierarchy.
// Mode sideband is equal-resource in both candidate and matched control.
// A raw packet uses two 32-bit words; compressed packet uses one.
// Sign extension is EXPLICIT to avoid mixed signed/unsigned SV expression bugs.
module v262_delta_decoder_proxy(
 input wire compressed,
 input wire [31:0] beat0,
 input wire [31:0] beat1,
 output wire [15:0] a0,a1,a2,a3
);
 wire [15:0] base = beat0[30:15];
 wire [15:0] d1sx = {{11{beat0[14]}},beat0[14:10]};
 wire [15:0] d2sx = {{11{beat0[9]}},beat0[9:5]};
 wire [15:0] d3sx = {{11{beat0[4]}},beat0[4:0]};
 assign a0 = compressed ? base : beat0[31:16];
 assign a1 = compressed ? (base + d1sx) : beat0[15:0];
 assign a2 = compressed ? (base + d2sx) : beat1[31:16];
 assign a3 = compressed ? (base + d3sx) : beat1[15:0];
endmodule
