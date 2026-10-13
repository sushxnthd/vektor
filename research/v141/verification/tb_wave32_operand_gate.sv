`timescale 1ns/1ps
module tb_wave32_operand_gate;
  localparam WIDTH=1024;
  reg [17:0] src_regs;
  reg [2:0] pending;
  reg [3*WIDTH-1:0] rf_values;
  reg wb_valid;
  reg [5:0] wb_reg;
  reg [WIDTH-1:0] wb_value;
  wire [2:0] ready_f, rf_read_f, ready_b, rf_read_b;
  wire [3*WIDTH-1:0] operands_f, operands_b;
  wire all_f, all_b;
  integer seed,n,lane,src,sel;
  reg hit,expected_ready_f,expected_ready_b,expected_read;
  reg [WIDTH-1:0] expected_f,expected_b;
  vektor_wave32_operand_gate #(.LANES(32),.BYPASS(1)) forwarded(
    .src_regs(src_regs),.pending(pending),.rf_values(rf_values),
    .wb_valid(wb_valid),.wb_reg(wb_reg),.wb_value(wb_value),
    .ready(ready_f),.rf_read(rf_read_f),.operands(operands_f),.all_ready(all_f)
  );
  vektor_wave32_operand_gate #(.LANES(32),.BYPASS(0)) baseline(
    .src_regs(src_regs),.pending(pending),.rf_values(rf_values),
    .wb_valid(wb_valid),.wb_reg(wb_reg),.wb_value(wb_value),
    .ready(ready_b),.rf_read(rf_read_b),.operands(operands_b),.all_ready(all_b)
  );
  task check_case;
    begin
      for(src=0;src<3;src=src+1) begin
        hit=wb_valid && (src_regs[src*6 +: 6]==wb_reg);
        expected_ready_f=!pending[src] || hit;
        expected_ready_b=!pending[src] && !hit;
        expected_read=!pending[src] && !hit;
        expected_f=expected_ready_f ? (hit ? wb_value : rf_values[src*WIDTH +: WIDTH]) : {WIDTH{1'b0}};
        expected_b=expected_ready_b ? rf_values[src*WIDTH +: WIDTH] : {WIDTH{1'b0}};
        if(ready_f[src] !== expected_ready_f ||
           ready_b[src] !== expected_ready_b ||
           rf_read_f[src] !== expected_read ||
           rf_read_b[src] !== expected_read ||
           operands_f[src*WIDTH +: WIDTH] !== expected_f ||
           operands_b[src*WIDTH +: WIDTH] !== expected_b)
           $fatal(1,"V141 operand mismatch case=%0d src=%0d",n,src);
      end
      if(all_f !== (&ready_f) || all_b !== (&ready_b))
        $fatal(1,"V141 all_ready mismatch case=%0d",n);
    end
  endtask
  initial begin
    seed=1415090;
    for(n=0;n<4096;n=n+1) begin
      src_regs[5:0]=$random(seed);
      src_regs[11:6]=$random(seed);
      src_regs[17:12]=$random(seed);
      pending=$random(seed);
      wb_valid=($random(seed)&1);
      sel=$random(seed);
      if(sel<0) sel=-(sel+1);
      if(($random(seed)&1)!=0) wb_reg=src_regs[(sel%3)*6 +: 6];
      else wb_reg=$random(seed);
      for(lane=0;lane<32;lane=lane+1) begin
        wb_value[lane*32 +: 32]=$random(seed);
        rf_values[lane*32 +: 32]=$random(seed);
        rf_values[(32+lane)*32 +: 32]=$random(seed);
        rf_values[(64+lane)*32 +: 32]=$random(seed);
      end
      #1;check_case();
    end
    $display("V141 PASS: 4096 cases x 3 sources x 32 lanes");
    $finish;
  end
endmodule
