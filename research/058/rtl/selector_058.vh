  integer best;
  reg urgent_found;
  reg [REMW-1:0] best_rem;
  always @* begin
    best=-1;
    urgent_found=1'b0;
    best_rem={REMW{1'b1}};
    for (integer k=0;k<N;k=k+1) begin
      if (k<count && q_age[k]>=AGE_LIMIT && !urgent_found) begin
        urgent_found=1'b1;
        best=k;
      end
    end
    if (!urgent_found) begin
      for (integer k=0;k<N;k=k+1) begin
        if (k<count && (best<0 || q_rem[k]<best_rem)) begin
          best=k;
          best_rem=q_rem[k];
        end
      end
    end
    pop_valid=(best>=0);
    pop_tag={TAGW{1'b0}};
    pop_data={DATAW{1'b0}};
    pop_remaining={REMW{1'b0}};
    pop_age={AGEW{1'b0}};
    pop_urgent=1'b0;
    if (best>=0) begin
      pop_tag=q_tag[best];
      pop_data=q_data[best];
      pop_remaining=q_rem[best];
      pop_age=q_age[best];
      pop_urgent=(q_age[best]>=AGE_LIMIT);
    end
  end
  wire pop_fire=pop_valid && pop_ready;
  assign push_ready=(count<N) || pop_fire;
  wire push_fire=push_valid && push_ready;
