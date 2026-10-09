// Vektor-055 experimental masked tagged operand collector.
// Two independent in-flight instructions, three sources each. NOT a complete RF.
// DEDUP=1 reads each distinct same-instruction physical register once.
// DEDUP=0 reads every logical source. Returns must be tagged (tag,operand,reg).
// No same-cycle zero-latency response: requests are acknowledged before return.
module rf_masked_fanout_055 #(
  parameter integer IDW=8, DW=32, TAGW=8, DEDUP=1
)(
  input wire clk, rst_n,
  input wire issue_valid,
  output reg issue_ready,
  input wire [TAGW-1:0] issue_tag,
  input wire [3*IDW-1:0] issue_regs,
  input wire [2:0] issue_mask,
  output reg req_valid,
  input wire req_ready,
  output reg [TAGW-1:0] req_tag,
  output reg [1:0] req_operand,
  output reg [IDW-1:0] req_reg,
  input wire resp_valid,
  input wire [TAGW-1:0] resp_tag,
  input wire [1:0] resp_operand,
  input wire [IDW-1:0] resp_reg,
  input wire [DW-1:0] resp_data,
  output reg complete_valid,
  input wire complete_ready,
  output reg [TAGW-1:0] complete_tag,
  output reg [3*DW-1:0] complete_data,
  output reg resp_error
);
  reg live[0:1];
  reg [TAGW-1:0] tags[0:1];
  reg [3*IDW-1:0] regs[0:1];
  reg [2:0] masks[0:1];
  reg [3*DW-1:0] data[0:1];
  reg [2:0] requested[0:1];
  reg [2:0] received[0:1];
  reg req_rr;
  integer s, o, j, k, ss, free_slot, req_slot, req_op, complete_slot;
  reg is_root;
  reg resp_found;
  reg [2:0] resp_fanout;
  integer resp_slot;

  always @* begin
    free_slot=-1;
    for (s=0;s<2;s=s+1)
      if (!live[s] && free_slot<0) free_slot=s;
    issue_ready=(free_slot>=0);
    for (s=0;s<2;s=s+1)
      if (live[s] && tags[s]==issue_tag) issue_ready=1'b0;

    req_valid=0; req_tag=0; req_operand=0; req_reg=0;
    req_slot=-1; req_op=-1;
    for (k=0;k<2;k=k+1) begin
      ss=(req_rr+k)%2;
      for (o=0;o<3;o=o+1) begin
        is_root=1;
        if (DEDUP!=0) begin
          for (j=0;j<o;j=j+1)
            if (masks[ss][j] && regs[ss][j*IDW +: IDW]==regs[ss][o*IDW +: IDW]) is_root=0;
        end
        if (req_slot<0 && live[ss] && masks[ss][o] && !requested[ss][o] && is_root) begin
          req_slot=ss; req_op=o;
          req_valid=1;
          req_tag=tags[ss];
          req_operand=o;
          req_reg=regs[ss][o*IDW +: IDW];
        end
      end
    end

    complete_valid=0; complete_tag=0; complete_data=0;
    complete_slot=-1;
    for (s=0;s<2;s=s+1)
      if (complete_slot<0 && live[s] && (&(received[s] | ~masks[s]))) begin
        complete_slot=s;
        complete_valid=1;
        complete_tag=tags[s];
        complete_data=data[s];
      end

    resp_found=0; resp_slot=-1; resp_fanout=0;
    for (s=0;s<2;s=s+1) begin
      if (live[s] && tags[s]==resp_tag && resp_slot<0) begin
        resp_slot=s;
        if (resp_operand<3 &&
            masks[s][resp_operand] && regs[s][resp_operand*IDW +: IDW]==resp_reg &&
            requested[s][resp_operand] && !received[s][resp_operand]) begin
          resp_found=1;
          for (o=0;o<3;o=o+1) begin
            if (DEDUP!=0) begin
              if (masks[s][o] && regs[s][o*IDW +: IDW]==resp_reg) resp_fanout[o]=1;
            end else if (o==resp_operand) resp_fanout[o]=1;
          end
        end
      end
    end
  end

  integer t;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      req_rr<=0;
      resp_error<=0;
      for (t=0;t<2;t=t+1) begin
        live[t]<=0; tags[t]<=0; regs[t]<=0; masks[t]<=0; data[t]<=0;
        requested[t]<=0; received[t]<=0;
      end
    end else begin
      if (complete_valid && complete_ready) live[complete_slot]<=0;
      if (issue_valid && issue_ready) begin
        live[free_slot]<=1;
        tags[free_slot]<=issue_tag;
        regs[free_slot]<=issue_regs;
        masks[free_slot]<=issue_mask;
        data[free_slot]<=0;
        requested[free_slot]<=0;
        received[free_slot]<=0;
      end
      if (req_valid && req_ready) begin
        requested[req_slot][req_op]<=1;
        req_rr<=!req_slot[0];
      end
      if (resp_valid) begin
        if (!resp_found) resp_error<=1;
        else begin
          for (t=0;t<3;t=t+1) begin
            if (resp_fanout[t]) begin
              received[resp_slot][t]<=1;
              data[resp_slot][t*DW +: DW]<=resp_data;
            end
          end
        end
      end
    end
  end
endmodule
