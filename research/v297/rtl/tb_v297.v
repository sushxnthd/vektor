// Independent Python oracle emits one expected grant for each clock cycle.
module tb_v297;
  reg clk=0, rst_n=0;
  reg [2:0] valid=0;
  reg [11:0] bank_a=0, bank_b=0;
  wire [2:0] candidate, rotating, maximum, compact, rotating_static;
  reg [2:0] expected_candidate, expected_rotating, expected_maximum;
  integer fd, n, cycles, errors;
  v297_bank_rescue_core #(.ROTATING(0)) dut0(
    .clk(clk),.rst_n(rst_n),.valid(valid),.bank_a(bank_a),.bank_b(bank_b),.grant(candidate));
  v297_bank_rescue_core #(.ROTATING(1)) dut1(
    .clk(clk),.rst_n(rst_n),.valid(valid),.bank_a(bank_a),.bank_b(bank_b),.grant(rotating));
  v297_maxpair_core dut2(
    .clk(clk),.rst_n(rst_n),.valid(valid),.bank_a(bank_a),.bank_b(bank_b),.grant(maximum));
  v297_maxpair_cooldown_core dut3(
    .clk(clk),.rst_n(rst_n),.valid(valid),.bank_a(bank_a),.bank_b(bank_b),.grant(compact));
  v297_rotating_static_core dut4(\n    .clk(clk),.rst_n(rst_n),.valid(valid),.bank_a(bank_a),.bank_b(bank_b),.grant(rotating_static));\n  initial begin
    cycles=0;errors=0;
    fd=$fopen("/tmp/v297_rtl_vectors.txt","r");
    if(fd==0) $fatal(1,"missing independent trace");
    rst_n=1; #1; rst_n=0; #2; rst_n=1;
    while(!$feof(fd)) begin
      n=$fscanf(fd,"%h %h %h %h %h %h\\n",valid,bank_a,bank_b,expected_candidate,expected_rotating,expected_maximum);
      if(n==6) begin
        #1;
        if(candidate !== expected_candidate || rotating !== expected_rotating || rotating_static !== expected_rotating || maximum !== expected_maximum || compact !== candidate) begin
          $display("MISMATCH cycle=%0d candidate=%b expected=%b rotating=%b expected=%b maximum=%b expected=%b",cycles,candidate,expected_candidate,rotating,expected_rotating,maximum,expected_maximum);
          errors=errors+1;
          if(errors>10) $fatal(1,"too many RTL mismatches");
        end
        clk=1; #1; clk=0; cycles=cycles+1;
      end
    end
    $fclose(fd);
    if(errors!=0 || cycles!=17832) $fatal(1,"RTL equivalence failed errors=%0d cycles=%0d",errors,cycles);
    $display("V297_RTL_EQUIVALENCE_PASS cycles=%0d",cycles);
    $finish;
  end
endmodule
