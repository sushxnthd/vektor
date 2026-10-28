// V297 sole active candidate and matched rotating-serial control.
// Three oldest requests, 16 banks, two read ports per bank, two issue slots.
// This is standalone synthesizable arbitration RTL, not a complete GPU tile.
module v297_bank_rescue_core #(
  parameter ROTATING = 0
) (
  input wire clk,
  input wire rst_n,
  input wire [2:0] valid,
  input wire [11:0] bank_a,
  input wire [11:0] bank_b,
  output wire [2:0] grant
);
  reg cooldown;
  reg [1:0] phase;

  // Four operand reads violate a two-port bank iff any triple aliases.
  function automatic fits_pair;
    input [3:0] a, b, c, d;
    begin
      fits_pair = !((a==b && a==c) ||
                    (a==b && a==d) ||
                    (a==c && a==d) ||
                    (b==c && b==d));
    end
  endfunction

  // Identical serial-greedy logic and port accounting for both contestants.
  function automatic [2:0] greedy;
    input [2:0] v;
    input [11:0] a, b;
    input [1:0] start;
    reg [2:0] g;
    integer step, idx, j, count;
    begin
      g=3'b000;
      count=0;
      for(step=0;step<3;step=step+1) begin
        idx=start+step;
        if(idx>=3) idx=idx-3;
        if(v[idx] && count<2) begin
          if(count==0) begin
            g[idx]=1'b1;
            count=count+1;
          end else begin
            for(j=0;j<3;j=j+1) begin
              if(g[j] && fits_pair(a[4*j +: 4],b[4*j +: 4],
                                   a[4*idx +: 4],b[4*idx +: 4])) begin
                g[idx]=1'b1;
                count=count+1;
              end
            end
          end
        end
      end
      greedy=g;
    end
  endfunction

  wire [2:0] serial_grants =
      greedy(valid,bank_a,bank_b,ROTATING ? phase : 2'd0);
  wire only_one = (serial_grants==3'b001 ||
                   serial_grants==3'b010 ||
                   serial_grants==3'b100);
  wire younger_pair_fits =
      fits_pair(bank_a[7:4],bank_b[7:4],bank_a[11:8],bank_b[11:8]);
  wire rescue = !ROTATING && !cooldown && only_one &&
                valid[1] && valid[2] && younger_pair_fits;
  assign grant = rescue ? 3'b110 : serial_grants;

  always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
      cooldown<=1'b0;
      phase<=2'd0;
    end else begin
      cooldown<=rescue;
      phase <= phase==2'd2 ? 2'd0 : phase+2'd1;
    end
  end
endmodule
