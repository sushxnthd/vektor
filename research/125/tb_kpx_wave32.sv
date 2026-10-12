`timescale 1ns/1ps
module tb_kpx_wave32;
    reg clk=0;
    always #5 clk=~clk;
    reg rst_n=1, valid_i=0;
    reg [31:0] initial_mask_i=32'hffffffff, imm_i=0;
    reg [3:0] opcode_i=0,rd_i=0,rs1_i=0,rs2_i=0,dbg_reg_i=0;
    reg [4:0] dbg_lane_i=0;
    wire ready_o,fault_o,commit_o;
    wire [31:0] mask_o,dbg_value_o;
    wire [3:0] depth_o;
    kpx_wave32_int dut(.*);
    integer fd,rc,op,rd,rs1,rs2,r,l,dep,checks=0,insts=0;
    reg [31:0] imm,expected;
    reg [31:0] mask_expected;
    reg [8*8-1:0] tag;
    task reset_wave(input [31:0] m);
        begin
            @(negedge clk); initial_mask_i=m; rst_n=0; valid_i=0;
            @(posedge clk); #1; rst_n=1;
        end
    endtask
    task issue(input [3:0] opc, input [3:0] d, input [3:0] a,
               input [3:0] b, input [31:0] immv);
        begin
            @(negedge clk);
            opcode_i=opc; rd_i=d; rs1_i=a; rs2_i=b; imm_i=immv; valid_i=1;
            #1;
            if (fault_o !== 1'b0 || commit_o !== 1'b1) $fatal(1,"unexpected fault at instruction %0d",insts);
            @(posedge clk); #1; valid_i=0; insts=insts+1;
        end
    endtask
    task rejected(input [3:0] opc);
        reg [31:0] before_mask;
        reg [3:0] before_depth;
        begin
            before_mask=mask_o; before_depth=depth_o;
            @(negedge clk); opcode_i=opc; valid_i=1;
            #1;
            if (fault_o !== 1'b1 || commit_o !== 1'b0) $fatal(1,"missing illegal-instruction fault");
            @(posedge clk); #1; valid_i=0;
            if (mask_o !== before_mask || depth_o !== before_depth) $fatal(1,"fault changed control state");
            checks=checks+1;
        end
    endtask
    initial begin
        fd=$fopen("research/125/vectors.txt","r");
        if (!fd) $fatal(1,"missing generated vectors.txt");
        while (!$feof(fd)) begin
            rc=$fscanf(fd,"%s",tag);
            if (rc != 1) begin
                if (!$feof(fd)) $fatal(1,"bad vector token");
            end else if (tag == "R") begin
                rc=$fscanf(fd,"%h",mask_expected);
                if (rc!=1) $fatal(1,"bad R");
                reset_wave(mask_expected);
            end else if (tag == "I") begin
                rc=$fscanf(fd,"%d %d %d %d %h",op,rd,rs1,rs2,imm);
                if (rc!=5) $fatal(1,"bad I");
                issue(op[3:0],rd[3:0],rs1[3:0],rs2[3:0],imm);
            end else if (tag == "C") begin
                rc=$fscanf(fd,"%h %d",mask_expected,dep);
                if (rc!=2) $fatal(1,"bad C");
                if (mask_o !== mask_expected || depth_o !== dep[3:0])
                    $fatal(1,"mask/depth mismatch instr=%0d mask=%h expected=%h depth=%0d expected=%0d",
                          insts,mask_o,mask_expected,depth_o,dep);
                checks=checks+1;
            end else if (tag == "D") begin
                rc=$fscanf(fd,"%d %d %h",r,l,expected);
                if (rc!=3) $fatal(1,"bad D");
                dbg_reg_i=r[3:0]; dbg_lane_i=l[4:0]; #1;
                if (dbg_value_o !== expected)
                    $fatal(1,"reg mismatch instr=%0d r%0d lane%0d got=%h expected=%h",insts,r,l,dbg_value_o,expected);
                checks=checks+1;
            end else if (tag == "E") begin
                rc=$fscanf(fd,"%d",op);
                if (rc!=1) $fatal(1,"bad E");
                rejected(op[3:0]);
            end else $fatal(1,"unknown vector tag %s",tag);
        end
        $fclose(fd);
        $display("V125 RTL PASS instructions=%0d checks=%0d",insts,checks);
        $finish;
    end
endmodule
