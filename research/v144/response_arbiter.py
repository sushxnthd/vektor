"""V144 work-conserving bank-aware RF response selector.
No arithmetic; software scheduling reference, not a hardware implementation.
"""
def completion_hint(item,active,ops,pc,coalesce):
    due,w,idx,val=item
    if w not in active:return False
    src=ops[pc[w]].src
    covered={i for i,r in enumerate(src) if coalesce and r==src[idx]} if coalesce else {idx}
    return len(set(active[w]['values'])|covered)==3

def priority(item,index,active,ops,pc,cycle,coalesce,policy):
    due,w,idx,val=item
    age=cycle-due
    if policy=='oldest_scan':return (0,0,-due,-index)
    if policy=='finish_first':
        return (int(age>=8),int(completion_hint(item,active,ops,pc,coalesce)),-due,-index)
    raise ValueError(policy)

def choose_responses(reads,ready_idx,active,ops,pc,mapping,cycle,global_limit,bank_limit,coalesce,policy):
    assert global_limit>=1 and bank_limit>=1
    order=sorted(ready_idx,key=lambda i:priority(reads[i],i,active,ops,pc,cycle,coalesce,policy),reverse=True)
    chosen=set();bank_counts={}
    for i in order:
        bank=mapping[ops[pc[reads[i][1]]].src[reads[i][2]]]
        if len(chosen)>=global_limit:break
        if bank_counts.get(bank,0)>=bank_limit:continue
        chosen.add(i);bank_counts[bank]=bank_counts.get(bank,0)+1
    return chosen
