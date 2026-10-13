`timescale 1ns/1ps
module tb_wave32_broadcast_capture;
  localparam WIDTH=1024;
  reg clk=0; always #5 clk=~clk;
  reg rst_n=0,clear=0,wb_valid=0;
  reg [17:0] src_regs=0;
  reg [5:0] wb_reg=0;
  reg [WIDTH-1:0] wb_value=0;
  wire [2:0] captured_valid;
  wire [3*WIDTH-1:0] captured_data;
  integer lane;
  vektor_wave32_broadcast_capture dut(
    .clk(clk),.rst_n(rst_n),.clear(clear),.src_regs(src_regs),
    .wb_valid(wb_valid),.wb_reg(wb_reg),.wb_value(wb_value),
    .captured_valid(captured_valid),.captured_data(captured_data)
  );
  task step; begin @(posedge clk); #1; end endtask
  initial begin
    step(); if(captured_valid!==0) $fatal(1,"reset");
    @(negedge clk); rst_n=1;src_regs={6'd7,6'd7,6'd7};
    wb_valid=1;wb_reg=7;
    for(lane=0;lane<32;lane=lane+1) wb_value[lane*32 +:32]=32'h12340000+lane;
    step();
    if(captured_valid!==3'b111) $fatal(1,"triple broadcast");
    if(captured_data[0 +: WIDTH]!==wb_value ||
       captured_data[WIDTH +: WIDTH]!==wb_value ||
       captured_data[2*WIDTH +: WIDTH]!==wb_value)
      $fatal(1,"32-lane data mismatch");
    @(negedge clk); wb_value=0;wb_reg=7;
    step();if(captured_data[0 +: WIDTH]===0) $fatal(1,"overwrite");
    @(negedge clk);clear=1;step();
    if(captured_valid!==0) $fatal(1,"clear");
    @(negedge clk);clear=0;src_regs={6'd8,6'd7,6'd7};wb_valid=1;wb_reg=7;
    step();if(captured_valid!==3'b011) $fatal(1,"double broadcast");
    @(negedge clk);wb_reg=8;step();
    if(captured_valid!==3'b111) $fatal(1,"late third operand");
    $display("V142 PASS: registered triple/double multicast, all 32 lanes, hold/clear");
    $finish;
  end
endmodule
