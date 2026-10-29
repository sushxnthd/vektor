// V301 bounded physicality probe: identical 4-lane, 8-entry storage.
// FULL_CAM=1 associative; FULL_CAM=0 two sets x four ways.
// set4 is functional, NOT a physically optimized banked baseline.
module v301_scoreboard_rtl #(
    parameter FULL_CAM = 1,
    parameter DEPTH = 8,
    parameter WARP_W = 6,
    parameter EPOCH_W = 8,
    parameter MASK_W = 8
)(
    input wire clk,
    input wire rst,
    input wire [3:0] in_valid,
    input wire [4*WARP_W-1:0] in_warp,
    input wire [4*EPOCH_W-1:0] in_epoch,
    input wire [4*MASK_W-1:0] in_mask,
    output reg [3:0] in_ready,
    output reg out_valid,
    output reg [WARP_W-1:0] out_warp,
    output reg [EPOCH_W-1:0] out_epoch,
    output reg [MASK_W-1:0] out_mask
);
    reg [WARP_W-1:0] q_w [0:DEPTH-1];
    reg [EPOCH_W-1:0] q_e [0:DEPTH-1];
    reg [MASK_W-1:0] q_m [0:DEPTH-1];
    reg [WARP_W-1:0] n_w [0:DEPTH-1];
    reg [EPOCH_W-1:0] n_e [0:DEPTH-1];
    reg [MASK_W-1:0] n_m [0:DEPTH-1];
    reg [3:0] q_count;
    reg [3:0] n_count;
    integer i, lane, j, hit, set_occupancy;
    reg blocked;
    reg [WARP_W-1:0] w;
    reg [EPOCH_W-1:0] e;
    reg [MASK_W-1:0] m;

    always @* begin
        out_valid = (q_count != 0);
        out_warp = out_valid ? q_w[0] : 0;
        out_epoch = out_valid ? q_e[0] : 0;
        out_mask = out_valid ? q_m[0] : 0;
        for (i=0; i<DEPTH; i=i+1) begin
            n_w[i] = q_w[i];
            n_e[i] = q_e[i];
            n_m[i] = q_m[i];
        end
        n_count = q_count;
        if (q_count != 0) begin
            for (i=0; i<DEPTH-1; i=i+1) begin
                n_w[i] = q_w[i+1];
                n_e[i] = q_e[i+1];
                n_m[i] = q_m[i+1];
            end
            n_w[DEPTH-1] = 0;
            n_e[DEPTH-1] = 0;
            n_m[DEPTH-1] = 0;
            n_count = q_count - 1'b1;
        end
        in_ready = 4'b0000;
        blocked = 1'b0;
        w = 0; e = 0; m = 0;
        hit = -1;
        set_occupancy = 0;
        for (lane=0; lane<4; lane=lane+1) begin
            w = in_warp[lane*WARP_W +: WARP_W];
            e = in_epoch[lane*EPOCH_W +: EPOCH_W];
            m = in_mask[lane*MASK_W +: MASK_W];
            if (!in_valid[lane]) begin
                in_ready[lane] = 1'b1;
            end else if (!blocked) begin
                hit = -1;
                set_occupancy = 0;
                for (j=0; j<DEPTH; j=j+1) begin
                    if (j < n_count) begin
                        if (n_w[j] == w && n_e[j] == e) hit = j;
                        if (n_w[j][0] == w[0]) set_occupancy = set_occupancy + 1;
                    end
                end
                if (hit >= 0) begin
                    n_m[hit] = n_m[hit] | m;
                    in_ready[lane] = 1'b1;
                end else if (n_count < DEPTH &&
                             (FULL_CAM || set_occupancy < (DEPTH/2))) begin
                    n_w[n_count] = w;
                    n_e[n_count] = e;
                    n_m[n_count] = m;
                    n_count = n_count + 1'b1;
                    in_ready[lane] = 1'b1;
                end else begin
                    blocked = 1'b1;
                end
            end
        end
    end
    integer k;
    always @(posedge clk) begin
        if (rst) begin
            q_count <= 0;
            for (k=0; k<DEPTH; k=k+1) begin
                q_w[k] <= 0;
                q_e[k] <= 0;
                q_m[k] <= 0;
            end
        end else begin
            q_count <= n_count;
            for (k=0; k<DEPTH; k=k+1) begin
                q_w[k] <= n_w[k];
                q_e[k] <= n_e[k];
                q_m[k] <= n_m[k];
            end
        end
    end
endmodule
