import io,os,subprocess,tempfile,unittest
from pathlib import Path
from trace_contract import FIELDS,read_trace
from patch_vortex import inject
ROOT=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_formatter(self):
  with tempfile.TemporaryDirectory() as d:
   binary=Path(d)/'probe';out=Path(d)/'out.csv'
   subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror','-I',str(ROOT),
       str(ROOT/'test_probe.cpp'),'-o',str(binary)],check=True)
   subprocess.run([str(binary)],env={**os.environ,'VEKTOR_LSU_TRACE':str(out)},check=True)
   rows=read_trace(io.StringIO(out.read_text()))
   self.assertEqual(len(rows),2)
   self.assertEqual(rows[0].hart,(2,1,0))
   self.assertEqual(rows[1].op,'F')
 def test_patch(self):
  with self.assertRaises(ValueError):inject('unrelated')
  stub='#include "lsu_unit.h"\n'+'\t\tstate.fence.engage(trace);\n\t\tDT(3, this->name() << " fence-lock: " << *trace);\n'+'\t\tlsu_req.uuid = trace->uuid;\n\n\t\t// send memory request\n'
  patched=inject(stub)
  self.assertIn('trace->cta_id',patched)
  with self.assertRaises(ValueError):inject(patched)
 def test_reject_bad_provenance(self):
  good='0,0,0,0,0,1,2,L,4096,4,G,virtual,lsu_issue\n'
  self.assertEqual(len(read_trace(io.StringIO(good))),1)
  for bad in [good.replace('virtual','physical'),good.replace('lsu_issue','retired'),
      good.replace(',4096,4,',',4097,4,'),good.replace(',G,',',U,'),good*2]:
   with self.assertRaises(ValueError):read_trace(io.StringIO(bad))
 def test_header(self):self.assertEqual(len(FIELDS),13)
if __name__=='__main__':unittest.main()
