"""Fail-closed audit of Vortex SimX trace CSV suitability for cohort experiments."""
import argparse,csv,json
from pathlib import Path
REQUIRED_INSTRUCTION={'uuid','PC','opcode','core_id','warp_id','tmask'}
REQUIRED_LANE={'lane_id','effective_address','memory_op','memory_order_epoch'}

def audit(path):
    with Path(path).open(newline='') as f:
        reader=csv.DictReader(f)
        columns=set(reader.fieldnames or [])
        rows=sum(1 for _ in reader)
    instr=REQUIRED_INSTRUCTION<=columns
    lane=REQUIRED_LANE<=columns
    return {'rows':rows,'columns':sorted(columns),
            'instruction_metadata_usable':instr,
            'coalescing_and_SC_replay_usable':instr and lane and rows>0,
            'missing_lane_fields':sorted(REQUIRED_LANE-columns),
            'status':'READY' if instr and lane and rows>0 else 'BLOCKED',
            'reason':('Complete lane-address and ordering schema' if instr and lane and rows>0
                      else 'No per-lane effective addresses and ordering epochs: instrument SimX LSU')}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('csv');a=ap.parse_args()
    result=audit(a.csv);print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['status']=='READY' else 2)
