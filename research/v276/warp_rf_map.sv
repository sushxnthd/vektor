module v276_warp_rf_map #(parameter ADAPTIVE=1, FIXED_MODE=0) (
input wire clk,rst,alloc_en,
input wire [1:0] alloc_warp,
input wire alloc_mode,
input wire valid0,valid1,
input wire [1:0] warp0,warp1,warpw,
input wire [5:0] reg0,reg1,regw,
output wire [1:0] bank0,bank1,bankw,
output wire [5:0] row0,row1,roww,
output wire grant0,grant1
);
reg [3:0] mode_latched;
always @(posedge clk) begin
 if(rst) mode_latched<=4'b0;
 else if(alloc_en) mode_latched[alloc_warp]<=alloc_mode;
end
wire mode0=ADAPTIVE?mode_latched[warp0]:FIXED_MODE;
wire mode1=ADAPTIVE?mode_latched[warp1]:FIXED_MODE;
wire modew=ADAPTIVE?mode_latched[warpw]:FIXED_MODE;
assign bank0=reg0[1:0]^(reg0[3:2]&{2{mode0}});
assign bank1=reg1[1:0]^(reg1[3:2]&{2{mode1}});
assign bankw=regw[1:0]^(regw[3:2]&{2{modew}});
assign row0={warp0,reg0[5:2]};
assign row1={warp1,reg1[5:2]};
assign roww={warpw,regw[5:2]};
assign grant0=valid0;
assign grant1=valid1&&(!valid0||(bank0!=bank1));
endmodule
