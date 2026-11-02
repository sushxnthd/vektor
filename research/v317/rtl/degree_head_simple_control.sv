// V317 adversarial *simple control*, not a promoted GPU architecture mechanism.
// Oldest-valid first; remaining requests in ascending static bank-conflict degree.
// Identical 4 request slots, 16 banks, 2 physical reads/bank and 2 charged reads/request.
// Reuses the exact V309 compact greedy admission logic after a 3-slot permutation.
// The permutation/sorting logic MUST be included in synthesis/PPA comparisons.
module vektor_v317_degree_head_arbiter (
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    output reg [3:0] grant
);
    // Pure functions: explicit operands are required by Yosys and ensure @*
    // reevaluates on bank-tag changes, not only on validity/order changes.
    function automatic [3:0] bank_at;
        input [15:0] flat;
        input [1:0] idx;
        begin bank_at = flat >> (idx * 4); end
    endfunction
    function automatic overlap;
        input [15:0] a_flat, b_flat;
        input [1:0] x, y;
        reg [3:0] ax, bx, ay, by;
        begin
            ax=bank_at(a_flat,x); bx=bank_at(b_flat,x);
            ay=bank_at(a_flat,y); by=bank_at(b_flat,y);
            overlap=(ax==ay) || (ax==by) || (bx==ay) || (bx==by);
        end
    endfunction

    reg [2:0] degree [0:3];
    reg [1:0] o1, o2, o3, temp;
    integer i, j;
    always @* begin
        for (i=0; i<4; i=i+1) begin
            degree[i]=0;
            for (j=0; j<4; j=j+1)
                if ((i!=j) && request_valid[j] &&
                    overlap(src0_bank_flat,src1_bank_flat,i[1:0],j[1:0]))
                    degree[i]=degree[i]+1'b1;
        end
        o1=2'd1; o2=2'd2; o3=2'd3;
        if ((degree[o2]<degree[o1]) ||
            ((degree[o2]==degree[o1]) && (o2<o1))) begin
            temp=o1; o1=o2; o2=temp;
        end
        if ((degree[o3]<degree[o2]) ||
            ((degree[o3]==degree[o2]) && (o3<o2))) begin
            temp=o2; o2=o3; o3=temp;
        end
        if ((degree[o2]<degree[o1]) ||
            ((degree[o2]==degree[o1]) && (o2<o1))) begin
            temp=o1; o1=o2; o2=temp;
        end
    end

    wire [3:0] pv = {request_valid[o3],request_valid[o2],
                     request_valid[o1],request_valid[0]};
    wire [15:0] pa = {bank_at(src0_bank_flat,o3),bank_at(src0_bank_flat,o2),
                      bank_at(src0_bank_flat,o1),bank_at(src0_bank_flat,2'd0)};
    wire [15:0] pb = {bank_at(src1_bank_flat,o3),bank_at(src1_bank_flat,o2),
                      bank_at(src1_bank_flat,o1),bank_at(src1_bank_flat,2'd0)};
    wire [3:0] pg;
    vektor_v309_compact_greedy_arbiter admit (
        .request_valid(pv),.src0_bank_flat(pa),.src1_bank_flat(pb),.grant(pg)
    );
    always @* begin
        grant=4'b0000;
        grant[0]=pg[0];
        grant[o1]=pg[1];
        grant[o2]=pg[2];
        grant[o3]=pg[3];
    end
endmodule
