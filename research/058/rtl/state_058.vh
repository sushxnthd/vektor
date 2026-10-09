  integer i;
  integer src;
  integer remaining_count;
  always @(posedge clk) begin
    if (!rst_n) begin
      count<=0;
      for (i=0;i<N;i=i+1) begin
        q_tag[i]<=0; q_data[i]<=0; q_rem[i]<=0; q_age[i]<=0;
      end
    end else begin
      count<=count - pop_fire + push_fire;
      remaining_count=count-pop_fire;
      for (i=0;i<N;i=i+1) begin
        src=i + ((pop_fire && i>=best) ? 1 : 0);
        if (i<remaining_count) begin
          q_tag[i]<=q_tag[src];
          q_data[i]<=q_data[src];
          q_rem[i]<=q_rem[src] - ((pop_fire && q_tag[src]==pop_tag && q_rem[src]!=0) ? 1'b1 : 1'b0);
          q_age[i]<= (q_age[src]<AGE_LIMIT) ? q_age[src]+1'b1 : q_age[src];
        end else if (i==remaining_count && push_fire) begin
          q_tag[i]<=push_tag;
          q_data[i]<=push_data;
          q_rem[i]<=push_remaining - ((pop_fire && push_tag==pop_tag && push_remaining!=0) ? 1'b1 : 1'b0);
          q_age[i]<=0;
        end else begin
          q_tag[i]<=0; q_data[i]<=0; q_rem[i]<=0; q_age[i]<=0;
        end
      end
    end
  end
