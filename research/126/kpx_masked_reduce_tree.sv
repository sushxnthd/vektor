// Vektor-126: KPX Wave32 masked unsigned modulo-2^32 reduction.
// Combinational, functionally equivalent to sequential modulo addition.
// No timing, area, or power guarantee; balanced trees are established prior art.
module kpx_masked_reduce_tree(
    input wire [31:0] active_mask_i,
    input wire [1023:0] lane_values_i,
    output wire [31:0] sum_o
);
    wire [31:0] node [1:63];
    for (genvar i=0; i<32; i=i+1) begin : leaves
        assign node[32+i] = active_mask_i[i] ? lane_values_i[i*32 +: 32] : 32'b0;
    end
    for (genvar i=1; i<32; i=i+1) begin : adders
        assign node[i] = node[2*i] + node[2*i+1];
    end
    assign sum_o = node[1];
endmodule
