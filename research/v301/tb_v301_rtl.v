`timescale 1ns/1ps
module tb_v301_rtl;
    parameter FULL_CAM = 1;
    reg clk=0;
    always #5 clk=~clk;
    reg rst=1;
    reg [91:0] stimulus [0:1023];
    reg [26:0] expected [0:1023];
    reg [91:0] word;
    wire [3:0] ready;
    wire ov;
    wire [5:0] ow;
    wire [7:0] oe, om;
    wire [26:0] observed = {om,oe,ow,ov,ready};
    integer i;
    v301_scoreboard_rtl #(.FULL_CAM(FULL_CAM)) dut (
        .clk(clk), .rst(rst),
        .in_valid(word[3:0]), .in_warp(word[27:4]),
        .in_epoch(word[59:28]), .in_mask(word[91:60]),
        .in_ready(ready), .out_valid(ov), .out_warp(ow),
        .out_epoch(oe), .out_mask(om)
    );
    initial begin
        word = 0;
        if (FULL_CAM) begin
            $readmemh("research/v301/rtl_vectors/stim_cam.hex",stimulus);
            $readmemh("research/v301/rtl_vectors/exp_cam.hex",expected);
        end else begin
            $readmemh("research/v301/rtl_vectors/stim_set4.hex",stimulus);
            $readmemh("research/v301/rtl_vectors/exp_set4.hex",expected);
        end
        repeat(2) @(posedge clk);
        @(negedge clk); rst=0;
        for(i=0;i<1024;i=i+1) begin
            @(negedge clk);
            word=stimulus[i];
            #1;
            if(observed !== expected[i]) begin
                $display("MISMATCH FULL_CAM=%0d cycle=%0d got=%07h expected=%07h input=%023h",FULL_CAM,i,observed,expected[i],word);
                $fatal(1,"RTL differs from independent cycle oracle");
            end
        end
        $display("PASS FULL_CAM=%0d 1024 oracle-checked cycles",FULL_CAM);
        $finish;
    end
endmodule
