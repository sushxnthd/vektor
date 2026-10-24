module tb_v291;
reg [3:0] valid;
reg [31:0] tag;
reg [31:0] data;
wire m_read,s_read;
wire [7:0] m_tag,s_tag;
wire [3:0] m_served,s_served;
wire [127:0] m_data,s_data;
integer v,p,i,first,checks;
reg [3:0] expected_m,expected_s;
reg [7:0] first_tag;
v291_multicast dut(valid,tag,data,m_read,m_tag,m_served,m_data);
v291_serial control(valid,tag,data,s_read,s_tag,s_served,s_data);
initial begin
  checks=0;data=32'hA1B2C3D4;valid=0;tag=0;
  for(v=0;v<16;v=v+1) begin
    for(p=0;p<256;p=p+1) begin
      valid=v;
      for(i=0;i<4;i=i+1) tag[i*8 +: 8]=(p>>(2*i))&3;
      #1;
      first=-1;first_tag=0;expected_m=0;expected_s=0;
      for(i=0;i<4;i=i+1) if(valid[i] && first<0) begin
        first=i;first_tag=tag[i*8 +: 8];
      end
      if(first>=0) begin
        expected_s[first]=1;
        for(i=0;i<4;i=i+1)
          if(valid[i] && tag[i*8 +: 8]==first_tag) expected_m[i]=1;
      end
      if(m_read!==(first>=0) || s_read!==(first>=0) ||
         m_served!==expected_m || s_served!==expected_s)
        $fatal(1,"grant mismatch valid=%h tags=%h m=%h s=%h",valid,tag,m_served,s_served);
      if(first>=0 && (m_tag!==first_tag || s_tag!==first_tag))
        $fatal(1,"tag mismatch");
      for(i=0;i<4;i=i+1) begin
        if(m_data[i*32 +: 32] !== (expected_m[i]?data:32'b0))
          $fatal(1,"multicast data mismatch");
        if(s_data[i*32 +: 32] !== (expected_s[i]?data:32'b0))
          $fatal(1,"serial data mismatch");
      end
      checks=checks+1;
    end
  end
  $display("V291 PASS %0d exhaustive 2-bit tag / valid cases",checks);
  $finish;
end
endmodule
