// Vektor-087: per-(bank,latency) round-robin future writeback reservation.
// Conditional class fairness only. No cancellation, completion identity, data or tags.
module rf_wb_reservation_087 #(
    parameter integer BANKS = 4,
    parameter integer BANK_W = 2,
    parameter integer REQS = 4,
    parameter integer LAT_W = 3,
    parameter integer MAX_LATENCY = 4,
    parameter integer WB_PORTS_PER_BANK = 1,
    parameter integer COUNT_W = (WB_PORTS_PER_BANK > 1) ? $clog2(WB_PORTS_PER_BANK + 1) : 1,
    parameter integer PTR_W = (REQS > 1) ? $clog2(REQS) : 1
)(
    input wire clk,
    input wire rst_n,
    input wire [REQS-1:0] req_valid,
    input wire [REQS*BANK_W-1:0] req_bank,
    input wire [REQS*LAT_W-1:0] req_latency,
    output reg [REQS-1:0] req_grant,
    output wire [BANKS*COUNT_W-1:0] due_count
);
    reg [COUNT_W-1:0] slots [0:MAX_LATENCY][0:BANKS-1];
    reg [PTR_W-1:0] rr_ptr [0:MAX_LATENCY-1][0:BANKS-1];
    reg [PTR_W-1:0] next_ptr [0:MAX_LATENCY-1][0:BANKS-1];
    integer b, l, k, idx, used;
    always @* begin
        req_grant = {REQS{1'b0}};
        idx = 0;
        used = 0;
        for (b=0; b<BANKS; b=b+1) begin
            for (l=1; l<=MAX_LATENCY; l=l+1) begin
                used = slots[l][b];
                next_ptr[l-1][b] = rr_ptr[l-1][b];
                for (k=0; k<REQS; k=k+1) begin
                    idx = rr_ptr[l-1][b] + k;
                    if (idx >= REQS) idx = idx - REQS;
                    if (rst_n && req_valid[idx] &&
                        req_bank[idx*BANK_W +: BANK_W] == b &&
                        req_latency[idx*LAT_W +: LAT_W] == l &&
                        used < WB_PORTS_PER_BANK) begin
                        req_grant[idx] = 1'b1;
                        used = used + 1;
                        if (idx == REQS-1)
                            next_ptr[l-1][b] = {PTR_W{1'b0}};
                        else
                            next_ptr[l-1][b] = idx + 1;
                    end
                end
            end
        end
    end

    integer sb, sl, si, next_used;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (sb=0; sb<BANKS; sb=sb+1) begin
                for (sl=0; sl<=MAX_LATENCY; sl=sl+1)
                    slots[sl][sb] <= {COUNT_W{1'b0}};
                for (sl=0; sl<MAX_LATENCY; sl=sl+1)
                    rr_ptr[sl][sb] <= {PTR_W{1'b0}};
            end
        end else begin
            for (sb=0; sb<BANKS; sb=sb+1) begin
                for (sl=0; sl<MAX_LATENCY; sl=sl+1) begin
                    next_used = slots[sl+1][sb];
                    for (si=0; si<REQS; si=si+1) begin
                        if (req_grant[si] &&
                            req_bank[si*BANK_W +: BANK_W] == sb &&
                            req_latency[si*LAT_W +: LAT_W] == sl+1)
                            next_used = next_used + 1;
                    end
                    slots[sl][sb] <= next_used[COUNT_W-1:0];
                    rr_ptr[sl][sb] <= next_ptr[sl][sb];
                end
                slots[MAX_LATENCY][sb] <= {COUNT_W{1'b0}};
            end
        end
    end

    genvar g;
    generate for (g=0; g<BANKS; g=g+1) begin : due_outputs
        assign due_count[g*COUNT_W +: COUNT_W] = slots[0][g];
    end endgenerate
`ifdef FORMAL
    integer fb, fl;
    always @(posedge clk) begin
        for (fb=0; fb<BANKS; fb=fb+1) begin
            for (fl=0; fl<=MAX_LATENCY; fl=fl+1)
                assert(slots[fl][fb] <= WB_PORTS_PER_BANK);
            for (fl=0; fl<MAX_LATENCY; fl=fl+1)
                assert(rr_ptr[fl][fb] < REQS);
        end
    end
`endif
endmodule
