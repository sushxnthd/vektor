// Independent port-counter oracle for parameter-scaling RTL. Neither
// contestant is used to construct expected grants. No workload holdouts read.
module tb_v296_scaling;
  parameter integer BANK_BITS=4;
  parameter integer SLOTS=4;
  localparam integer BANKS=(1 << BANK_BITS);
  reg [SLOTS-1:0] request_valid;
  reg [SLOTS*BANK_BITS-1:0] bank0,bank1;
  wire [SLOTS-1:0] grant_pair,grant_mask;
  integer used [0:BANKS-1];
  integer seed,trial,s,k,ba,bb;
  reg [SLOTS-1:0] expected;

  v296_pairwise_scaling #(.BANK_BITS(BANK_BITS),.SLOTS(SLOTS)) pair(
    .request_valid(request_valid),.bank0(bank0),.bank1(bank1),.grant(grant_pair)
  );
  v296_onehot_scaling #(.BANK_BITS(BANK_BITS),.SLOTS(SLOTS)) mask(
    .request_valid(request_valid),.bank0(bank0),.bank1(bank1),.grant(grant_mask)
  );

  task check_oracle;
    begin
      expected=0;
      for(k=0;k<BANKS;k=k+1) used[k]=0;
      for(k=0;k<SLOTS;k=k+1) begin
        ba=bank0[k*BANK_BITS +: BANK_BITS];
        bb=bank1[k*BANK_BITS +: BANK_BITS];
        if(request_valid[k]) begin
          if(ba==bb) begin
            if(used[ba]==0) begin
              expected[k]=1'b1;
              used[ba]=used[ba]+2;
            end
          end else if(used[ba]<2 && used[bb]<2) begin
            expected[k]=1'b1;
            used[ba]=used[ba]+1;
            used[bb]=used[bb]+1;
          end
        end
      end
      #1;
      if(grant_pair !== expected || grant_mask !== expected)
        $fatal(1,"V296_SCALING_ORACLE_FAIL bits=%0d slots=%0d trial=%0d valid=%h bank0=%h bank1=%h expected=%h pair=%h mask=%h",
               BANK_BITS,SLOTS,trial,request_valid,bank0,bank1,expected,grant_pair,grant_mask);
    end
  endtask

  initial begin
    seed=296; request_valid=0; bank0=0; bank1=0;
    // Exhaust all 2^10 possible inputs for (4 banks, 2 slots).
    if(BANK_BITS==2 && SLOTS==2) begin
      for(trial=0;trial<1024;trial=trial+1) begin
        request_valid=trial & 3;
        bank0[0 +: BANK_BITS]=(trial >> 2) & 3;
        bank1[0 +: BANK_BITS]=(trial >> 4) & 3;
        bank0[BANK_BITS +: BANK_BITS]=(trial >> 6) & 3;
        bank1[BANK_BITS +: BANK_BITS]=(trial >> 8) & 3;
        check_oracle;
      end
    end
    for(trial=0;trial<4096;trial=trial+1) begin
      request_valid=$random(seed);
      if(trial%13==0) request_valid={SLOTS{1'b1}};
      if(trial%17==0) request_valid=0;
      for(s=0;s<SLOTS;s=s+1) begin
        case(trial%6)
          0: begin
            bank0[s*BANK_BITS +: BANK_BITS]=0;
            bank1[s*BANK_BITS +: BANK_BITS]=0;
          end
          1: begin
            bank0[s*BANK_BITS +: BANK_BITS]=s % BANKS;
            bank1[s*BANK_BITS +: BANK_BITS]=(s+1) % BANKS;
          end
          2: begin
            bank0[s*BANK_BITS +: BANK_BITS]=s % BANKS;
            bank1[s*BANK_BITS +: BANK_BITS]=s % BANKS;
          end
          3: begin
            bank0[s*BANK_BITS +: BANK_BITS]=$random(seed);
            bank1[s*BANK_BITS +: BANK_BITS]=bank0[s*BANK_BITS +: BANK_BITS];
          end
          default: begin
            bank0[s*BANK_BITS +: BANK_BITS]=$random(seed);
            bank1[s*BANK_BITS +: BANK_BITS]=$random(seed);
          end
        endcase
      end
      check_oracle;
    end
    $display("V296_SCALING_ORACLE_PASS bits=%0d slots=%0d random=4096 exhaustive=%0d",
             BANK_BITS,SLOTS,(BANK_BITS==2 && SLOTS==2)?1024:0);
    $finish;
  end
endmodule
