module vektor_warp_scheduler (
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

    reg [2:0] rr0;
    reg [2:0] rr1;
    reg [2:0] rr2;
    reg [2:0] rr3;

    reg [3:0] pick0;
    reg [3:0] pick1;
    reg [3:0] pick2;
    reg [3:0] pick3;

    function [3:0] pick_ready;
        input [7:0] eligible;
        input [2:0] start;
        integer k;
        integer idx;
        reg found;
        begin
            pick_ready = 4'b0000;
            found = 1'b0;
            for (k = 0; k < 8; k = k + 1) begin
                idx = (start + k) & 7;
                if (!found && eligible[idx]) begin
                    pick_ready[3] = 1'b1;
                    pick_ready[2:0] = idx;
                    found = 1'b1;
                end
            end
        end
    endfunction

    always @* begin
        pick0 = pick_ready(wave_valid[7:0]   & wave_ready[7:0],   rr0);
        pick1 = pick_ready(wave_valid[15:8]  & wave_ready[15:8],  rr1);
        pick2 = pick_ready(wave_valid[23:16] & wave_ready[23:16], rr2);
        pick3 = pick_ready(wave_valid[31:24] & wave_ready[31:24], rr3);

        issue_valid = {pick3[3], pick2[3], pick1[3], pick0[3]};
        issue_wave0 = {2'b00, pick0[2:0]};
        issue_wave1 = 5'd8  + {2'b00, pick1[2:0]};
        issue_wave2 = 5'd16 + {2'b00, pick2[2:0]};
        issue_wave3 = 5'd24 + {2'b00, pick3[2:0]};
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rr0 <= 3'd0;
            rr1 <= 3'd0;
            rr2 <= 3'd0;
            rr3 <= 3'd0;
        end else begin
            if (pick0[3]) rr0 <= pick0[2:0] + 3'd1;
            if (pick1[3]) rr1 <= pick1[2:0] + 3'd1;
            if (pick2[3]) rr2 <= pick2[2:0] + 3'd1;
            if (pick3[3]) rr3 <= pick3[2:0] + 3'd1;
        end
    end

endmodule
