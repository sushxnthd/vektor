// Sequential FIFO trace validation for the existing two-wide reference.
// Distinct from the exhaustive combinational truth table: this checks
// queue advancement and conservation over complete bank-request streams.
module v317_fifo_pair_trace_tb;
  reg head_valid, next_valid, downstream_ready;
  reg [3:0] head_bank, next_bank;
  wire issue_head, issue_next;
  integer mode, cycle, cursor, issued, n, expected, collisions;
  reg [3:0] stream [0:63];
  v317_fifo_pair_reference dut (
    .head_valid(head_valid), .head_bank(head_bank),
    .next_valid(next_valid), .next_bank(next_bank),
    .downstream_ready(downstream_ready),
    .issue_head(issue_head), .issue_next(issue_next)
  );
  initial begin
    head_valid=0; next_valid=0; downstream_ready=0;
    head_bank=0; next_bank=0;
    for (mode=0; mode<4; mode=mode+1) begin
      for (n=0; n<64; n=n+1) begin
        case(mode)
          0: stream[n]=n%2; // alternating
          1: stream[n]=(n<32)?0:1; // clustered, same marginals
          2: stream[n]=0; // complete collision
          3: stream[n]=n%4; // four-bank cycle
        endcase
      end
      cursor=0; cycle=0; issued=0; collisions=0;
      while (cursor<64 && cycle<128) begin
        head_valid=(cursor<64);
        next_valid=(cursor+1<64);
        head_bank=stream[cursor];
        if (cursor+1<64) next_bank=stream[cursor+1];
        else next_bank=0;
        downstream_ready=1;
        #1;
        expected=1;
        if (next_valid && head_bank!=next_bank) expected=2;
        if (issue_head!==1'b1 || issue_next!==(expected==2))
          $fatal(1,"grant mismatch mode=%0d cycle=%0d",mode,cycle);
        if (expected==1 && next_valid) collisions=collisions+1;
        cursor=cursor+expected;
        issued=issued+expected;
        cycle=cycle+1;
      end
      if (issued!=64 || cursor!=64)
        $fatal(1,"conservation failure mode=%0d issued=%0d",mode,issued);
      case(mode)
        0: if (cycle!=32) $fatal(1,"alternating expected 32 got %0d",cycle);
        1: if (cycle!=63) $fatal(1,"clustered expected 63 got %0d",cycle);
        2: if (cycle!=64) $fatal(1,"single bank expected 64 got %0d",cycle);
        3: if (cycle!=32) $fatal(1,"four bank expected 32 got %0d",cycle);
      endcase
      $display("mode=%0d cycles=%0d issued=%0d collisions=%0d",mode,cycle,issued,collisions);
    end
    $display("PASS four 64-request FIFO traces");
    $finish;
  end
endmodule
