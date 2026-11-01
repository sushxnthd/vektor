// Independent operand-count oracle for parameterized S/B scaling experiment.
// Run with iverilog -Ptb_v317_sb_scaling.S=... -Ptb_v317_sb_scaling.B=...
module tb_v317_sb_scaling;
    parameter integer S = 4;
    parameter integer B = 16;
    localparam integer W = $clog2(B);
    reg [S-1:0] request_valid;
    reg [S*W-1:0] src0_bank_flat, src1_bank_flat;
    wire [S-1:0] grant_mask, grant_pair;
    integer reads [0:B-1];
    integer seed, t, s, a, b, code, temp, mask, k, checks;
    reg [S-1:0] expected;

    v317_bankmask_param #(.S(S),.B(B)) mask_impl (
        .request_valid(request_valid), .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat), .grant(grant_mask));
    v317_pairwise_param #(.S(S),.B(B)) pair_impl (
        .request_valid(request_valid), .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat), .grant(grant_pair));

    task automatic verify;
        integer n, x, y, q;
        reg [S-1:0] gold;
        begin
            gold = {S{1'b0}};
            for (q = 0; q < B; q = q + 1)
                reads[q] = 0;
            for (n = 0; n < S; n = n + 1) begin
                x = src0_bank_flat[n*W +: W];
                y = src1_bank_flat[n*W +: W];
                if (request_valid[n] && reads[x] + (x == y) <= 1 &&
                    reads[y] + (x == y) <= 1) begin
                    gold[n] = 1'b1;
                    reads[x] = reads[x] + 1;
                    reads[y] = reads[y] + 1;
                end
            end
            #1;
            if (grant_mask !== gold || grant_pair !== gold)
                $fatal(1,"S=%0d B=%0d valid=%b a=%h b=%h expected=%b mask=%b pair=%b",
                    S,B,request_valid,src0_bank_flat,src1_bank_flat,gold,grant_mask,grant_pair);
            checks = checks + 1;
        end
    endtask

    initial begin
        seed = 317042 + S*100 + B;
        checks = 0;
        request_valid = {S{1'b0}};
        src0_bank_flat = {S*W{1'b0}};
        src1_bank_flat = {S*W{1'b0}};
        #1;
        // Directed all-bank-conflict and all-inactive controls.
        request_valid = {S{1'b1}};
        verify();
        request_valid = {S{1'b0}};
        verify();
        if (S == 2 && B == 4) begin
            for (mask = 0; mask < 4; mask = mask + 1) begin
                request_valid = mask;
                for (code = 0; code < 256; code = code + 1) begin
                    temp = code;
                    for (s = 0; s < S; s = s + 1) begin
                        src0_bank_flat[s*W +: W] = temp % B;
                        temp = temp / B;
                        src1_bank_flat[s*W +: W] = temp % B;
                        temp = temp / B;
                    end
                    verify();
                end
            end
        end
        for (t = 0; t < 2048; t = t + 1) begin
            request_valid = $random(seed);
            for (s = 0; s < S; s = s + 1) begin
                src0_bank_flat[s*W +: W] = $random(seed);
                src1_bank_flat[s*W +: W] = $random(seed);
            end
            verify();
        end
        if (checks != 2050 + ((S == 2 && B == 4) ? 1024 : 0))
            $fatal(1,"wrong check count %0d",checks);
        $display("PASS V317 S/B scaling S=%0d B=%0d independent checks=%0d",S,B,checks);
        $finish;
    end
endmodule
