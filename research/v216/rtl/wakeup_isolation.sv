// V216: shared-predecode control versus group-isolated wakeup tags.
// Test vehicle only; no physical qualification is implied.
module vektor_wakeup_predecoded (
  input wire valid, input wire [4:0] wave, input wire [7:0] tag,
  input wire [127:0] pending, input wire [1023:0] entry_tags,
  output wire [127:0] hit
);
  wire [3:0] grp;
  genvar g, i;
  generate for (g=0;g<4;g=g+1) begin: groups
    assign grp[g] = valid && (wave[4:3] == g);
  end
  for (i=0;i<128;i=i+1) begin: ent
    assign hit[i] = grp[i/32] && pending[i] && (wave[2:0] == ((i/4)%8)) &&
                    (tag == entry_tags[i*8 +: 8]);
  end endgenerate
endmodule

module vektor_wakeup_isolated (
  input wire valid, input wire [4:0] wave, input wire [7:0] tag,
  input wire [127:0] pending, input wire [1023:0] entry_tags,
  output wire [127:0] hit
);
  wire [3:0] grp;
  wire [7:0] local_tag [0:3];
  genvar g, i;
  generate for (g=0;g<4;g=g+1) begin: groups
    assign grp[g] = valid && (wave[4:3] == g);
    assign local_tag[g] = tag & {8{grp[g]}};
  end
  for (i=0;i<128;i=i+1) begin: ent
    assign hit[i] = grp[i/32] && pending[i] && (wave[2:0] == ((i/4)%8)) &&
                    (local_tag[i/32] == entry_tags[i*8 +: 8]);
  end endgenerate
endmodule
