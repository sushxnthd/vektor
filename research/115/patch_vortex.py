"""Pinned Vortex SimX MMU paired VA/PA instrumentation.

H=translated enqueue on TLB miss; T=successful TLB hit output;
B=bypass output; F=fault/killed (PA=0, not an address).
This does not instrument lane provenance or physical memory completion.
"""
from pathlib import Path
import argparse,shutil,subprocess
PIN='7fe19369587c087f902c3e2bc2add612aa910a95'
HERE=Path(__file__).resolve().parent

def inject(s):
    edits=[
        ('#include "mmu.h"\n','#include "mmu.h"\n#include "vektor_mmu_probe.h"\n'),
        ('void Mmu::kill_request(uint32_t port, const MemReq& req) {\n',
         'void Mmu::kill_request(uint32_t port, const MemReq& req) {\n'
         '  vektor_mmu_probe::emit(req.uuid, req.hart_id, req.tag, port, req.addr, 0, \'F\');\n'),
        ('        translated.addr = (ppn << VX_VM_PAGE_LOG2_SIZE) | (req.addr & page_mask);\n'
         '        replay_.at(port).push(translated);\n',
         '        translated.addr = (ppn << VX_VM_PAGE_LOG2_SIZE) | (req.addr & page_mask);\n'
         '        vektor_mmu_probe::emit(req.uuid, req.hart_id, req.tag, port, req.addr, translated.addr, \'H\');\n'
         '        replay_.at(port).push(translated);\n'),
        ('    if (!needs_translation(req)) {\n'
         '      if (ReqOut.at(p).try_send(req)) {\n'
         '        ReqIn.at(p).pop();\n',
         '    if (!needs_translation(req)) {\n'
         '      if (ReqOut.at(p).try_send(req)) {\n'
         '        vektor_mmu_probe::emit(req.uuid, req.hart_id, req.tag, p, req.addr, req.addr, \'B\');\n'
         '        ReqIn.at(p).pop();\n'),
        ('      if (ReqOut.at(p).try_send(translated)) {\n'
         '        ReqIn.at(p).pop();\n',
         '      if (ReqOut.at(p).try_send(translated)) {\n'
         '        vektor_mmu_probe::emit(req.uuid, req.hart_id, req.tag, p, req.addr, translated.addr, \'T\');\n'
         '        ReqIn.at(p).pop();\n')]
    for before,after in edits:
        if s.count(before)!=1:raise ValueError('MMU source anchor mismatch '+repr(before[:90]))
        s=s.replace(before,after)
    return s

def main():
    ap=argparse.ArgumentParser();ap.add_argument('vortex_checkout',type=Path);args=ap.parse_args()
    root=args.vortex_checkout.resolve()
    sha=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    if sha!=PIN:raise SystemExit('Refusing unpinned upstream '+sha)
    p=root/'sim/simx/mem/mmu.cpp';h=root/'sim/simx/mem/vektor_mmu_probe.h'
    if h.exists():raise SystemExit('Probe header already exists')
    patched=inject(p.read_text())
    p.write_text(patched)
    shutil.copyfile(HERE/'vektor_mmu_probe.h',h)
    print('MMU translation-pair instrumentation installed; compile/run NOT established')
if __name__=='__main__':main()
