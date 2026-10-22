// Reproducible cycle-level RTL equivalence. This is NOT electrical validation.
module tb;
  reg clk2x=0, clk=0, phase=0, rst=1;
  reg rd_en0=0,rd_en1=0,wr_en=0;
  reg [3:0] rd_addr0=0,rd_addr1=0,wr_addr=0;
  reg [31:0] wr_data=0;
  wire p0,p1,c0,c1;
  wire [31:0] pd0,pd1,cd0,cd1;
  reg [31:0] reference [0:15];
  reg [31:0] e0,e1;
  integer k,seed=32'h13579BDF, n=0, failures=0;
  v272_pumped_rf pump(clk2x,phase,rst,rd_en0,rd_en1,rd_addr0,rd_addr1,wr_en,wr_addr,wr_data,p0,p1,pd0,pd1);
  v272_two_read_rf control(clk,rst,rd_en0,rd_en1,rd_addr0,rd_addr1,wr_en,wr_addr,wr_data,c0,c1,cd0,cd1);
  task tick;
    begin
      phase=0; clk2x=0; clk=0; #2;
      clk2x=1; clk=1; #2; clk2x=0; clk=0; #2;
      phase=1; clk2x=1; #2; clk2x=0; #2;
    end
  endtask
  task compare;
    begin
      if (p0 !== c0 || p1 !== c1 || p0 !== rd_en0 || p1 !== rd_en1) begin
        $display("VALID mismatch at %0d: %b%b vs %b%b",n,p0,p1,c0,c1); failures=failures+1;
      end
      if (rd_en0 && (pd0 !== cd0 || pd0 !== e0)) begin
        $display("PORT0 mismatch at %0d: pump=%h ctrl=%h exp=%h",n,pd0,cd0,e0); failures=failures+1;
      end
      if (rd_en1 && (pd1 !== cd1 || pd1 !== e1)) begin
        $display("PORT1 mismatch at %0d: pump=%h ctrl=%h exp=%h",n,pd1,cd1,e1); failures=failures+1;
      end
    end
  endtask
  initial begin
    tick(); rst=0;
    // Initialize all addresses with deterministic values before any read.
    for(k=0;k<16;k=k+1) begin
      wr_en=1; wr_addr=k; wr_data=32'hABCD0000+k;
      rd_en0=0; rd_en1=0;
      tick(); reference[k]=wr_data;
    end
    for(k=0;k<12000;k=k+1) begin
      rd_en0=($random(seed)&3)!=0;
      rd_en1=($random(seed)&3)!=0;
      rd_addr0=$random(seed); rd_addr1=$random(seed);
      wr_en=($random(seed)&7)==0;
      wr_addr=$random(seed); wr_data=$random(seed);
      // Reference is write-first for both phase reads.
      e0=(wr_en && wr_addr==rd_addr0)?wr_data:reference[rd_addr0];
      e1=(wr_en && wr_addr==rd_addr1)?wr_data:reference[rd_addr1];
      tick(); compare();
      if(wr_en) reference[wr_addr]=wr_data;
      n=n+1;
    end
    if(failures!=0) begin $display("FAIL: %0d mismatches in %0d cycles",failures,n); $fatal(1); end
    $display("PASS: %0d matched randomized core cycles",n); $finish;
  end
endmodule
