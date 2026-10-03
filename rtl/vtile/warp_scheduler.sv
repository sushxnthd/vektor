module vektor_warp_scheduler #(
    parameter integer NUM_WAVES = 32,
    parameter integer ISSUE_WIDTH = 4,
    parameter integer WAVE_ID_WIDTH = 5
) (
    input  logic                                clk,
    input  logic                                rst_n,
    input  logic [NUM_WAVES-1:0]                wave_valid,
    input  logic [NUM_WAVES-1:0]                wave_ready,
    output logic [ISSUE_WIDTH-1:0]               issue_valid,
    output logic [ISSUE_WIDTH-1:0][WAVE_ID_WIDTH-1:0] issue_wave_id
);

    logic [WAVE_ID_WIDTH-1:0] rr_ptr;
    logic [WAVE_ID_WIDTH-1:0] rr_next;
    logic [NUM_WAVES-1:0] selected;

    integer scan;
    integer idx;
    integer slot;

    always_comb begin
        issue_valid = '0;
        issue_wave_id = '0;
        selected = '0;
        rr_next = rr_ptr;
        slot = 0;

        for (scan = 0; scan < NUM_WAVES; scan = scan + 1) begin
            idx = (rr_ptr + scan) % NUM_WAVES;
            if ((slot < ISSUE_WIDTH) && wave_valid[idx] && wave_ready[idx] && !selected[idx]) begin
                issue_valid[slot] = 1'b1;
                issue_wave_id[slot] = idx[WAVE_ID_WIDTH-1:0];
                selected[idx] = 1'b1;
                rr_next = (idx + 1) % NUM_WAVES;
                slot = slot + 1;
            end
        end
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            rr_ptr <= '0;
        else
            rr_ptr <= rr_next;
    end

endmodule
