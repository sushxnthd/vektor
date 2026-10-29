`timescale 1ns/1ps
module tb_v307_issue_select;
    reg clk=0;
    always #5 clk=~clk;
    reg rst_n=0;
    reg [4:0] ready=0,next_valid=0;
    reg [39:0] current_banks=0,next_banks=0;
    wire [4:0] sel0,sel1,sel2;
    reg [4:0] exp0,exp1,exp2;
    integer fd,n,rc;
    v307_issue_select #(.MODE(0)) a(clk,rst_n,ready,next_valid,current_banks,next_banks,sel0);
    v307_issue_select #(.MODE(1)) b(clk,rst_n,ready,next_valid,current_banks,next_banks,sel1);
    v307_issue_select #(.MODE(2)) c(clk,rst_n,ready,next_valid,current_banks,next_banks,sel2);
    initial begin
        fd=$fopen("research/v307/rtl_vectors.txt","r");
        if(fd==0) $fatal(1,"vectors not found");
        @(negedge clk); rst_n=1;
        n=0;
        while(!$feof(fd)) begin
            @(negedge clk);
            rc=$fscanf(fd,"%h %h %h %h %h %h %h\n",ready,next_valid,current_banks,next_banks,exp0,exp1,exp2);
            if(rc==7) begin
                @(posedge clk); #1;
                if(sel0!==exp0 || sel1!==exp1 || sel2!==exp2)
                    $fatal(1,"Mismatch vector %0d max=%h/%h pressure=%h/%h future=%h/%h",n,sel0,exp0,sel1,exp1,sel2,exp2);
                n=n+1;
            end
        end
        if(n!=256) $fatal(1,"Wrong vector count %0d",n);
        $display("V307 clocked RTL oracle PASS %0d vectors, all three modes",n);
        $finish;
    end
endmodule
