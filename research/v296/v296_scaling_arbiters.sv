// V296 scaling study: same greedy two-read-port bank admission, parameterized.
// No scheduler, wave selector, storage, additional ports or throughput mechanism.
// See SCALING_CROSSOVER_PREREG_20261024.md. Synthesis compares both arbiters
// with exactly the same request and bank-index input/output widths.
module v296_pairwise_scaling #(
  parameter integer BANK_BITS = 4,
  parameter integer SLOTS = 4
)(
  input wire [SLOTS-1:0] request_valid,
  input wire [SLOTS*BANK_BITS-1:0] bank0,
  input wire [SLOTS*BANK_BITS-1:0] bank1,
  output reg [SLOTS-1:0] grant
);
  localparam integer HIT_BITS = $clog2(2*SLOTS+1);
  integer i,j;
  reg [BANK_BITS-1:0] a,b,pa,pb;
  reg [HIT_BITS-1:0] hits_a,hits_b;
  always @* begin
    grant=0; a=0; b=0; pa=0; pb=0; hits_a=0; hits_b=0;
    for(i=0;i<SLOTS;i=i+1) begin
      a=bank0[i*BANK_BITS +: BANK_BITS];
      b=bank1[i*BANK_BITS +: BANK_BITS];
      hits_a=0; hits_b=0;
      for(j=0;j<SLOTS;j=j+1) begin
        if(j<i && grant[j]) begin
          pa=bank0[j*BANK_BITS +: BANK_BITS];
          pb=bank1[j*BANK_BITS +: BANK_BITS];
          if(pa==a) hits_a=hits_a+1'b1;
          if(pb==a) hits_a=hits_a+1'b1;
          if(pa==b) hits_b=hits_b+1'b1;
          if(pb==b) hits_b=hits_b+1'b1;
        end
      end
      if(request_valid[i]) begin
        if(a==b) begin
          if(hits_a==0) grant[i]=1'b1;
        end else if(hits_a<2 && hits_b<2) grant[i]=1'b1;
      end
    end
  end
endmodule

// Strong equal-I/O-width serial one-hot occupancy control, matching V295
// PREDECODE=0 admission semantics without its scheduler/wave-index selectors.
module v296_onehot_scaling #(
  parameter integer BANK_BITS = 4,
  parameter integer SLOTS = 4
)(
  input wire [SLOTS-1:0] request_valid,
  input wire [SLOTS*BANK_BITS-1:0] bank0,
  input wire [SLOTS*BANK_BITS-1:0] bank1,
  output reg [SLOTS-1:0] grant
);
  localparam integer BANKS = (1 << BANK_BITS);
  reg [BANKS-1:0] once,twice,a,b;
  reg fit;
  integer i;
  always @* begin
    grant=0; once=0; twice=0; a=0; b=0; fit=0;
    for(i=0;i<SLOTS;i=i+1) begin
      a={{(BANKS-1){1'b0}},1'b1} << bank0[i*BANK_BITS +: BANK_BITS];
      b={{(BANKS-1){1'b0}},1'b1} << bank1[i*BANK_BITS +: BANK_BITS];
      fit=0;
      if(request_valid[i]) begin
        if(|(a&b)) fit=((once&a)==0);
        else fit=((twice&a)==0)&&((twice&b)==0);
        if(fit) begin
          grant[i]=1'b1;
          if(|(a&b)) begin
            once=once|a; twice=twice|a;
          end else begin
            twice=twice|(once&(a|b));
            once=once|a|b;
          end
        end
      end
    end
  end
endmodule
