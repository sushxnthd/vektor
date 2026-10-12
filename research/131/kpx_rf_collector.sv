// Vektor-131: original, synthesizable scalar operand-collector slice.
// Two RF banks, one read request per bank per cycle; one resident instruction.
// This is NOT a Wave32 register file, a V-Tile, or a physically validated GPU.
// The external RF must return each accepted read exactly once with its tag and
// transaction ID; it must not signal flush_ack until all pre-flush replies are
// discarded. rf_pending_i prevents reads of registers awaiting older writes.
module kpx_rf_collector #(
    parameter integer ADDR_W = 4,
    parameter integer TXN_W = 16
) (
    input  wire                    clk,
    input  wire                    rst_n,
    input  wire                    flush_ack_i,
    output wire                    flush_wait_o,
    input  wire                    instr_valid_i,
    output wire                    instr_ready_o,
    input  wire [2:0]              src_valid_i,
    input  wire [3*ADDR_W-1:0]     src_addr_i,
    input  wire [(1<<ADDR_W)-1:0]  rf_pending_i,
    output reg  [1:0]              rf_req_valid_o,
    output reg  [2*ADDR_W-1:0]     rf_req_addr_o,
    output reg  [3:0]              rf_req_tag_o,
    output wire [2*TXN_W-1:0]     rf_req_txn_o,
    input  wire [1:0]              rf_rsp_valid_i,
    input  wire [3:0]              rf_rsp_tag_i,
    input  wire [2*TXN_W-1:0]     rf_rsp_txn_i,
    input  wire [63:0]             rf_rsp_data_i,
    output wire                    done_valid_o,
    input  wire                    done_ready_i,
    output wire [95:0]             operands_o,
    output wire [TXN_W-1:0]       txn_o
);
    reg active_q;
    reg draining_q;
    reg [TXN_W-1:0] seq_q;
    reg [TXN_W-1:0] txn_q;
    reg [2:0] valid_q;
    reg [3*ADDR_W-1:0] addr_q;
    reg [2:0] held_q;
    reg [2:0] requested_q;
    reg [31:0] data_q [0:2];
    wire [ADDR_W-1:0] a0 = addr_q[0*ADDR_W +: ADDR_W];
    wire [ADDR_W-1:0] a1 = addr_q[1*ADDR_W +: ADDR_W];
    wire [ADDR_W-1:0] a2 = addr_q[2*ADDR_W +: ADDR_W];
    wire [ADDR_W-1:0] addr [0:2];
    assign addr[0] = a0;
    assign addr[1] = a1;
    assign addr[2] = a2;
    assign flush_wait_o = draining_q;
    assign instr_ready_o = rst_n && !draining_q && !active_q;
    assign done_valid_o = rst_n && active_q && (&held_q);
    assign operands_o = {data_q[2], data_q[1], data_q[0]};
    assign txn_o = txn_q;
    assign rf_req_txn_o = {txn_q,txn_q};

    integer i;
    integer b;
    reg earlier_alias;
    always @* begin
        rf_req_valid_o = 2'b00;
        rf_req_addr_o = {2*ADDR_W{1'b0}};
        rf_req_tag_o = 4'b0;
        earlier_alias = 1'b0;
        if (rst_n && !draining_q && active_q) begin
            for (integer k=0; k<3; k=k+1) begin
                earlier_alias = 1'b0;
                for (integer j=0; j<k; j=j+1)
                    if (valid_q[j] && addr[j] == addr[k])
                        earlier_alias = 1'b1;
                if (valid_q[k] && !earlier_alias && !held_q[k] &&
                    !requested_q[k] && !rf_pending_i[addr[k]]) begin
                    if (!rf_req_valid_o[addr[k][0]]) begin
                        rf_req_valid_o[addr[k][0]] = 1'b1;
                        rf_req_addr_o[addr[k][0]*ADDR_W +: ADDR_W] = addr[k];
                        rf_req_tag_o[addr[k][0]*2 +: 2] = k[1:0];
                    end
                end
            end
        end
    end

    always @(posedge clk) begin
        if (!rst_n) begin
            active_q <= 1'b0;
            draining_q <= 1'b1;
            seq_q <= {TXN_W{1'b0}};
            txn_q <= {TXN_W{1'b0}};
            valid_q <= 3'b0;
            addr_q <= {3*ADDR_W{1'b0}};
            held_q <= 3'b111;
            requested_q <= 3'b0;
            for (i=0; i<3; i=i+1) data_q[i] <= 32'b0;
        end else if (draining_q) begin
            // Outstanding replies are ignored until external RF proves drain.
            if (flush_ack_i) draining_q <= 1'b0;
        end else begin
            if (done_valid_o && done_ready_i) begin
                active_q <= 1'b0;
            end else if (instr_valid_i && instr_ready_o) begin
                active_q <= 1'b1;
                valid_q <= src_valid_i;
                addr_q <= src_addr_i;
                held_q <= ~src_valid_i;
                requested_q <= 3'b0;
                txn_q <= seq_q;
                seq_q <= seq_q + {{(TXN_W-1){1'b0}},1'b1};
                for (i=0; i<3; i=i+1) data_q[i] <= 32'b0;
            end else if (active_q) begin
                for (b=0; b<2; b=b+1) begin
                    if (rf_req_valid_o[b])
                        requested_q[rf_req_tag_o[b*2 +: 2]] <= 1'b1;
                    if (rf_rsp_valid_i[b] &&
                        rf_rsp_txn_i[b*TXN_W +: TXN_W] == txn_q &&
                        rf_rsp_tag_i[b*2 +: 2] < 3) begin
                        for (i=0; i<3; i=i+1) begin
                            if (valid_q[i] &&
                                addr[i] == addr[rf_rsp_tag_i[b*2 +: 2]] &&
                                requested_q[rf_rsp_tag_i[b*2 +: 2]]) begin
                                held_q[i] <= 1'b1;
                                data_q[i] <= rf_rsp_data_i[b*32 +: 32];
                            end
                        end
                    end
                end
            end
        end
    end
endmodule
