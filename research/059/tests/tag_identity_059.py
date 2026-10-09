"""Vektor-059 response-ID ambiguity demonstration (stdlib only)."""
from math import ceil,log2
import json
from pathlib import Path
# Two worlds with different operand meanings but identical tag-only packets.
a={'op0':165,'op1':182}
b={'op0':182,'op1':165}
obs_a=[(7,a[k]) for k in ('op0','op1')]
obs_b=[(7,b[k]) for k in ('op1','op0')]
assert obs_a==obs_b and a!=b
assert [(7,int(k[-1]),a[k]) for k in ('op0','op1')]!=[(7,int(k[-1]),b[k]) for k in ('op1','op0')]
records=[((w<<3)|slot,(((w<<3)|slot)<<2)|op) for w in range(32) for slot in range(8) for op in range(3)]
assert len(records)==768
assert len({x[0] for x in records})==256
assert len({x[1] for x in records})==768
assert max(x[1] for x in records)<1024
# A finite generation field alone does not protect against unbounded late duplicates.
assert (4&3)==0
result={'ambiguous_worlds':2,'maximum_responses':768,'instruction_only_tags':256,'instruction_only_collisions':512,'minimum_global_id_bits':ceil(log2(768)),'composite_ids':768,'two_bit_epoch_wrap_after_reuses':4,'scope':'hypothetical 32x8x3 globally merged returns; structural, not RTL or silicon'}
p=Path(__file__).resolve().parents[1]/'results';p.mkdir(exist_ok=True)
(p/'tag_identity_059.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
