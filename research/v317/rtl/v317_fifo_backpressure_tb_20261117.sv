// Backpressure and FIFO-conservation adversarial control.
// Research reference only; not a V296 physical implementation.
module v317_fifo_backpressure_tb;
  reg head_valid, next_valid, downstream_ready;
  reg [3:0] head_bank, next_bank;
  wire issue_head, issue_next;
  reg [3:0] stream [0:95];
  integer mode, cycle, cursor, advance, issued, stalls, i;
  v317_fifo_pair_reference dut (
    .head_valid(head_valid), .head_bank(head_bank),
    .next_valid(next_valid), .next_bank(next_bank),
    .downstream_ready(downstream_ready),
    .issue_head(issue_head), .issue_next(issue_next)
  );
  initial begin
    head_valid=0; next_valid=0; downstream_ready=0;
    head_bank=0; next_bank=0;
    for (mode=0;mode<4;mode=mode+1) begin
      for(i=0;i<96;i=i+1) begin
        case(mode)
          0: stream[i]=i%4;
          1: stream[i]=(i<48)?0:1;
          2: stream[i]=0;
          3: stream[i]=((i*7+i/3)%4);
        endcase
      end
      cursor=0; cycle=0; issued=0; stalls=0;
      while(cursor<96 && cycle<512) begin
        head_valid=cursor<96;
        next_valid=cursor+1<96;
        head_bank=stream[cursor];
        if(next_valid) next_bank=stream[cursor+1];
        else next_bank=0;
        // Deterministic, nonperiodic with respect to bank pattern.
        downstream_ready=((cycle*13+cycle/7+mode*3)%11)<7;
        #1;
        if(!downstream_ready) begin
          stalls=stalls+1;
          if(issue_head!==1'b0 || issue_next!==1'b0)
            $fatal(1,"issued during stall mode=%0d cycle=%0d",mode,cycle);
          advance=0;
        end else begin
          if(issue_head!==1'b1)
            $fatal(1,"lost head grant mode=%0d cycle=%0d",mode,cycle);
          advance=1;
          if(next_valid && head_bank!=next_bank) advance=2;
          if(issue_next!==(advance==2))
            $fatal(1,"illegal pair mode=%0d cycle=%0d",mode,cycle);
        end
        cursor=cursor+advance;
        issued=issued+advance;
        cycle=cycle+1;
      end
      if(cursor!=96 || issued!=96 || stalls==0)
        $fatal(1,"conservation/timeout mode=%0d cursor=%0d issued=%0d stalls=%0d",
               mode,cursor,issued,stalls);
      $display("mode=%0d cycles=%0d issued=%0d stalls=%0d",mode,cycle,issued,stalls);
    end
    $display("PASS backpressure FIFO conservation");
    $finish;
  end
endmodule
