#!/usr/bin/env node
"use strict";
/* V296 routed-area staircase fragility: retrospective, exact-integer audit.
 Run: node research/v296/routed_area_packing_fragility.js --self-test
 Provenance: matched extracted-RC run 40309580865, candidate artifact 12648648864
 SHA256 057d4fe6d4bf67164857c54c9635c302e163da6b486f59515b7b8151578d8388,
 serial fifth-stage artifact 12655030936
 SHA256 1ea4affb6c1f583a775aa9ee084a9c6dcd0b7856d5b8fa1850693f2f05617f67.
 Original archive validation is separate; this is a frozen-scalar audit.
 Not a physically replicated GPU tile or measured speedup.
*/
const SCALE=1000000n, A=17857644252n, S=18953830505n;
const guard=0.05;
const physical={
 candidate:{setup:-1.047895,hold:-0.036622,cap:3,slew:0,drc:0},
 serial:{setup:-1.859922,hold:-0.019796,cap:3,slew:0,drc:0}
};
function ceilDiv(n,d){if(n<0n||d<=0n)throw RangeError("invalid fraction");return (n+d-1n)/d;}
function adjusted(p=0n,q=0n){
 if(p<0n||q<0n||q>=SCALE)throw RangeError("invalid perturbation");
 return {a:A*(SCALE+p),s:S*(SCALE-q)};
}
function copies(n,a,s){if(n<0n||a<=0n||s<=0n)throw RangeError("invalid area");return n*s/a;}
function threshold(a,s){if(a<=0n||s<=0n)throw RangeError("invalid area");return a>=s?null:ceilDiv(a,s-a);}
function enumeration(n,a,s){
 let used=0n,count=0n;while(used+a<=n*s){used+=a;count++;}return count;
}
function physicalPass(x){return x.setup>=guard&&x.hold>=0&&x.cap===0&&x.slew===0&&x.drc===0;}
function selfTest(){
 if(threshold(A,S)!==17n||copies(16n,A,S)!==16n||copies(17n,A,S)!==18n)throw Error("base staircase");
 if(physicalPass(physical.candidate)||physicalPass(physical.serial))throw Error("false closure");
 for(const [p,q] of [[0n,0n],[1000n,0n],[2500n,0n],[5000n,5000n],[20000n,0n]]){
   const {a,s}=adjusted(p,q);
   for(let n=0n;n<=200n;n++)if(copies(n,a,s)!==enumeration(n,a,s))throw Error("enumeration mismatch");
   const t=threshold(a,s);
   if(t!==null&&(copies(t-1n,a,s)>t-1n||copies(t,a,s)<t+1n))throw Error("threshold mismatch");
 }
 if(copies(17n,adjusted(2400n).a,adjusted(2400n).s)!==18n)throw Error("0.24pct boundary");
 if(copies(17n,adjusted(2500n).a,adjusted(2500n).s)!==17n)throw Error("0.25pct boundary");
 if(threshold(S,S)!==null||threshold(S+1n,S)!==null)throw Error("negative control");
 for(const bad of [()=>adjusted(-1n),()=>adjusted(0n,SCALE),()=>copies(-1n,A,S),()=>threshold(0n,S)]){
   let rejected=false;try{bad();}catch(e){rejected=true;}if(!rejected)throw Error("bad input accepted");
 }
 return "ROUTED_AREA_PACKING_FRAGILITY_SELFTEST_PASS";
}
function evaluate(){
 const budget=17n*S,used=18n*A,remaining=budget-used;
 if(remaining<=0n)throw Error("no headroom");
 function row(p,q){const z=adjusted(p,q),t=threshold(z.a,z.s);
   return {candidate_plus_pct:Number(p)/10000,serial_minus_pct:Number(q)/10000,
     candidate_copies_at_17_serial_budget:Number(copies(17n,z.a,z.s)),
     first_extra_serial_budget:t===null?null:Number(t)};
 }
 return {
  evidence_tier:"RETROSPECTIVE_POSTROUTE_SCALAR_SENSITIVITY_NOT_TILE",
  candidate_area_um2:Number(A)/1e6,serial_area_um2:Number(S)/1e6,
  budget_17_serial_um2:Number(budget)/1e6,
  used_18_candidate_um2:Number(used)/1e6,
  remaining_um2:Number(remaining)/1e6,
  remaining_per_candidate_um2:Number(remaining)/18e6,
  maximum_candidate_area_increase_pct:Number(remaining)/Number(used)*100,
  nominal_first_extra_budget:Number(threshold(A,S)),
  candidate_physical_gate:physicalPass(physical.candidate)?"PASS":"FAIL",
  serial_physical_gate:physicalPass(physical.serial)?"PASS":"FAIL",
  candidate_setup_guard_shortfall_ns:guard-physical.candidate.setup,
  serial_setup_guard_shortfall_ns:guard-physical.serial.setup,
  candidate_only:[0n,1000n,2000n,2400n,2500n,5000n,10000n,20000n,50000n].map(p=>row(p,0n)),
  symmetric_adverse:[0n,1000n,2500n,5000n,10000n].map(p=>row(p,p)),
  limitations:"No multi-slice floorplan, wiring, clock tree, SRAM, power grid, bandwidth, feasible clock or performance validation. Both single-slice designs fail setup, hold and cap gates."
 };
}
if(typeof process!=="undefined"&&typeof require!=="undefined"&&require.main===module){
 if(process.argv.includes("--self-test"))console.log(selfTest());
 console.log(JSON.stringify(evaluate(),null,2));
}
