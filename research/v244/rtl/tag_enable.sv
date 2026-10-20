module miss_gated_tag_enable #(parameter TAG_W=4)(
  input logic [TAG_W-1:0] req_tag,tag0,tag1,
  input logic valid0,valid1,
  output logic hit,way,read_en0,read_en1
);
  logic h0,h1;
  always_comb begin
    h0=valid0&&(req_tag==tag0);
    h1=valid1&&(req_tag==tag1)&&!h0;
    hit=h0||h1; way=h1; read_en0=h0; read_en1=h1;
  end
endmodule
module phased_equal_resource_control #(parameter TAG_W=4)(
  input logic [TAG_W-1:0] req_tag,tag0,tag1,
  input logic valid0,valid1,
  output logic hit,way,read_en0,read_en1
);
  logic [1:0] matches;
  always_comb begin
    matches[0]=valid0&&(req_tag==tag0);
    matches[1]=valid1&&(req_tag==tag1);
    read_en0=matches[0]; read_en1=matches[1]&&!matches[0];
    hit=read_en0||read_en1; way=read_en1;
  end
endmodule
