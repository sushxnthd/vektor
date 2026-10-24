// V291 isolated one-bank read multicast. E0 until matched physical validation.
module v291_multicast #(parameter TAG_W=8, DATA_W=32)(
  input wire [3:0] valid,
  input wire [4*TAG_W-1:0] tag,
  input wire [DATA_W-1:0] rf_data,
  output reg rf_read,
  output reg [TAG_W-1:0] rf_tag,
  output reg [3:0] served,
  output reg [4*DATA_W-1:0] consumer_data
);
integer i, first;
always @* begin
  first=-1; rf_read=0; rf_tag=0; served=0; consumer_data=0;
  for(i=0;i<4;i=i+1) if(valid[i] && first<0) first=i;
  if(first>=0) begin
    rf_read=1;
    rf_tag=tag[first*TAG_W +: TAG_W];
    for(i=0;i<4;i=i+1)
      if(valid[i] && tag[i*TAG_W +: TAG_W]==rf_tag) begin
        served[i]=1;
        consumer_data[i*DATA_W +: DATA_W]=rf_data;
      end
  end
end
endmodule

// Serial same-port reference, NOT a matched-area architectural control.
module v291_serial #(parameter TAG_W=8, DATA_W=32)(
  input wire [3:0] valid,
  input wire [4*TAG_W-1:0] tag,
  input wire [DATA_W-1:0] rf_data,
  output reg rf_read,
  output reg [TAG_W-1:0] rf_tag,
  output reg [3:0] served,
  output reg [4*DATA_W-1:0] consumer_data
);
integer i, first;
always @* begin
  first=-1; rf_read=0; rf_tag=0; served=0; consumer_data=0;
  for(i=0;i<4;i=i+1) if(valid[i] && first<0) first=i;
  if(first>=0) begin
    rf_read=1;
    rf_tag=tag[first*TAG_W +: TAG_W];
    served[first]=1;
    consumer_data[first*DATA_W +: DATA_W]=rf_data;
  end
end
endmodule
