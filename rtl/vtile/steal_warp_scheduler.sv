module vektor_steal_warp_scheduler (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] wave_valid,
    input  wire [31:0] wave_ready,
    input  wire [3:0]  issue_accept,
    output reg  [3:0]  issue_valid,
    output reg  [4:0]  issue_wave0,
    output reg  [4:0]  issue_wave1,
    output reg  [4:0]  issue_wave2,
    output reg  [4:0]  issue_wave3
);

    reg [2:0] rr0, rr1, rr2, rr3;
    reg [3:0] p0, p1, p2, p3;
    reg [3:0] b0, b1, b2, b3;
    reg [7:0] e0, e1, e2, e3;
    reg [7:0] r0, r1, r2, r3;

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
        e0 = wave_valid[7:0]   & wave_ready[7:0];
        e1 = wave_valid[15:8]  & wave_ready[15:8];
        e2 = wave_valid[23:16] & wave_ready[23:16];
        e3 = wave_valid[31:24] & wave_ready[31:24];

        p0 = pick_ready(e0, rr0);
        p1 = pick_ready(e1, rr1);
        p2 = pick_ready(e2, rr2);
        p3 = pick_ready(e3, rr3);

        r0 = e0;
        r1 = e1;
        r2 = e2;
        r3 = e3;
        if (p0[3]) r0[p0[2:0]] = 1'b0;
        if (p1[3]) r1[p1[2:0]] = 1'b0;
        if (p2[3]) r2[p2[2:0]] = 1'b0;
        if (p3[3]) r3[p3[2:0]] = 1'b0;

        b0 = pick_ready(r0, rr0);
        b1 = pick_ready(r1, rr1);
        b2 = pick_ready(r2, rr2);
        b3 = pick_ready(r3, rr3);

        issue_valid = {p3[3], p2[3], p1[3], p0[3]};
        issue_wave0 = {2'b00, p0[2:0]};
        issue_wave1 = 5'd8  + {2'b00, p1[2:0]};
        issue_wave2 = 5'd16 + {2'b00, p2[2:0]};
        issue_wave3 = 5'd24 + {2'b00, p3[2:0]};

        // Each partition may donate one backup candidate into an otherwise
        // idle issue slot. Selection is combinational; fairness state changes
        // only when downstream logic asserts issue_accept for that slot.
        if (b0[3]) begin
            if (!issue_valid[0]) begin issue_valid[0] = 1'b1; issue_wave0 = {2'b00, b0[2:0]}; end
            else if (!issue_valid[1]) begin issue_valid[1] = 1'b1; issue_wave1 = {2'b00, b0[2:0]}; end
            else if (!issue_valid[2]) begin issue_valid[2] = 1'b1; issue_wave2 = {2'b00, b0[2:0]}; end
            else if (!issue_valid[3]) begin issue_valid[3] = 1'b1; issue_wave3 = {2'b00, b0[2:0]}; end
        end
        if (b1[3]) begin
            if (!issue_valid[0]) begin issue_valid[0] = 1'b1; issue_wave0 = 5'd8 + {2'b00, b1[2:0]}; end
            else if (!issue_valid[1]) begin issue_valid[1] = 1'b1; issue_wave1 = 5'd8 + {2'b00, b1[2:0]}; end
            else if (!issue_valid[2]) begin issue_valid[2] = 1'b1; issue_wave2 = 5'd8 + {2'b00, b1[2:0]}; end
            else if (!issue_valid[3]) begin issue_valid[3] = 1'b1; issue_wave3 = 5'd8 + {2'b00, b1[2:0]}; end
        end
        if (b2[3]) begin
            if (!issue_valid[0]) begin issue_valid[0] = 1'b1; issue_wave0 = 5'd16 + {2'b00, b2[2:0]}; end
            else if (!issue_valid[1]) begin issue_valid[1] = 1'b1; issue_wave1 = 5'd16 + {2'b00, b2[2:0]}; end
            else if (!issue_valid[2]) begin issue_valid[2] = 1'b1; issue_wave2 = 5'd16 + {2'b00, b2[2:0]}; end
            else if (!issue_valid[3]) begin issue_valid[3] = 1'b1; issue_wave3 = 5'd16 + {2'b00, b2[2:0]}; end
        end
        if (b3[3]) begin
            if (!issue_valid[0]) begin issue_valid[0] = 1'b1; issue_wave0 = 5'd24 + {2'b00, b3[2:0]}; end
            else if (!issue_valid[1]) begin issue_valid[1] = 1'b1; issue_wave1 = 5'd24 + {2'b00, b3[2:0]}; end
            else if (!issue_valid[2]) begin issue_valid[2] = 1'b1; issue_wave2 = 5'd24 + {2'b00, b3[2:0]}; end
            else if (!issue_valid[3]) begin issue_valid[3] = 1'b1; issue_wave3 = 5'd24 + {2'b00, b3[2:0]}; end
        end
    end

    // Advance a partition only for work that actually passed downstream
    // admission. If two accepted slots came from the same partition, the
    // later slot deterministically sets the next round-robin position.
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rr0 <= 3'd0;
            rr1 <= 3'd0;
            rr2 <= 3'd0;
            rr3 <= 3'd0;
        end else begin
            if (issue_valid[0] && issue_accept[0]) begin
                case (issue_wave0[4:3])
                    2'd0: rr0 <= issue_wave0[2:0] + 3'd1;
                    2'd1: rr1 <= issue_wave0[2:0] + 3'd1;
                    2'd2: rr2 <= issue_wave0[2:0] + 3'd1;
                    2'd3: rr3 <= issue_wave0[2:0] + 3'd1;
                endcase
            end
            if (issue_valid[1] && issue_accept[1]) begin
                case (issue_wave1[4:3])
                    2'd0: rr0 <= issue_wave1[2:0] + 3'd1;
                    2'd1: rr1 <= issue_wave1[2:0] + 3'd1;
                    2'd2: rr2 <= issue_wave1[2:0] + 3'd1;
                    2'd3: rr3 <= issue_wave1[2:0] + 3'd1;
                endcase
            end
            if (issue_valid[2] && issue_accept[2]) begin
                case (issue_wave2[4:3])
                    2'd0: rr0 <= issue_wave2[2:0] + 3'd1;
                    2'd1: rr1 <= issue_wave2[2:0] + 3'd1;
                    2'd2: rr2 <= issue_wave2[2:0] + 3'd1;
                    2'd3: rr3 <= issue_wave2[2:0] + 3'd1;
                endcase
            end
            if (issue_valid[3] && issue_accept[3]) begin
                case (issue_wave3[4:3])
                    2'd0: rr0 <= issue_wave3[2:0] + 3'd1;
                    2'd1: rr1 <= issue_wave3[2:0] + 3'd1;
                    2'd2: rr2 <= issue_wave3[2:0] + 3'd1;
                    2'd3: rr3 <= issue_wave3[2:0] + 3'd1;
                endcase
            end
        end
    end

endmodule
