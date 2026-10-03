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

    reg [4:0] rr_ptr;
    reg [4:0] rr_next;
    reg [31:0] selected;

    integer scan;
    integer idx;
    integer slot;

    always @* begin
        issue_valid = 4'b0000;
        issue_wave0 = 5'd0;
        issue_wave1 = 5'd0;
        issue_wave2 = 5'd0;
        issue_wave3 = 5'd0;
        selected = 32'b0;
        rr_next = rr_ptr;
        slot = 0;

        for (scan = 0; scan < 32; scan = scan + 1) begin
            idx = (rr_ptr + scan) & 31;
            if ((slot < 4) && wave_valid[idx] && wave_ready[idx] && !selected[idx]) begin
                issue_valid[slot] = 1'b1;
                case (slot)
                    0: issue_wave0 = idx;
                    1: issue_wave1 = idx;
                    2: issue_wave2 = idx;
                    3: issue_wave3 = idx;
                endcase
                selected[idx] = 1'b1;
                rr_next = (idx + 1) & 31;
                slot = slot + 1;
            end
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            rr_ptr <= 5'd0;
        else
            rr_ptr <= rr_next;
    end

endmodule
