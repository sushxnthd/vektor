module vektor_global_warp_scheduler (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] wave_valid,
    input  wire [31:0] wave_ready,
    output reg  [3:0]  issue_valid,
    output reg  [4:0]  issue_wave0,
    output reg  [4:0]  issue_wave1,
    output reg  [4:0]  issue_wave2,
    output reg  [4:0]  issue_wave3
);

    reg [4:0] rr;
    reg [4:0] last_pick;
    integer k;
    integer idx;
    integer count;

    always @* begin
        issue_valid = 4'b0000;
        issue_wave0 = 5'd0;
        issue_wave1 = 5'd0;
        issue_wave2 = 5'd0;
        issue_wave3 = 5'd0;
        last_pick = rr;
        count = 0;

        // Scan the 32-wave ready set once from the round-robin pointer and
        // admit the first four eligible waves. This is intentionally a wide
        // arbitration baseline; physical cost is measured separately.
        for (k = 0; k < 32; k = k + 1) begin
            idx = (rr + k) & 31;
            if (count < 4 && wave_valid[idx] && wave_ready[idx]) begin
                case (count)
                    0: begin issue_valid[0] = 1'b1; issue_wave0 = idx[4:0]; end
                    1: begin issue_valid[1] = 1'b1; issue_wave1 = idx[4:0]; end
                    2: begin issue_valid[2] = 1'b1; issue_wave2 = idx[4:0]; end
                    default: begin issue_valid[3] = 1'b1; issue_wave3 = idx[4:0]; end
                endcase
                last_pick = idx[4:0];
                count = count + 1;
            end
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            rr <= 5'd0;
        else if (issue_valid != 4'b0000)
            rr <= last_pick + 5'd1;
    end

endmodule
