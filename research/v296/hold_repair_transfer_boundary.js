#!/usr/bin/env node
"use strict";
// Prospective, conditional V296 hold-repair sensitivity. Not OpenROAD results.
// All timing is integer milli-ps; all area is integer micro-um^2.
const B = Object.freeze({"candidateSetup_mps":74236,"candidateHold_mps":-12622,"serialSetup_mps":-751540,"serialHold_mps":-9430,"setupGuard_mps":50000,"candidateArea_micro":13379001906,"serialArea_micro":15779651363});
function ceilDiv(a,b){if(!Number.isSafeInteger(a)||!Number.isSafeInteger(b)||a<0||b<=0)throw Error("invalid division");return Math.floor((a+b-1)/b)}
function analyze(p){
  for(const k of ["effectiveDelay_mps","holdEfficiency_ppm","setupCoupling_ppm","holdAdverse_mps","setupAdverse_mps","candidateAreaAdded_micro"])if(!Number.isSafeInteger(p[k])||p[k]<0)throw Error("invalid nonnegative integer "+k);
  if(p.holdEfficiency_ppm>1000000||p.setupCoupling_ppm>3000000)throw Error("unphysical declared model range");
  const recovered=Math.floor(p.effectiveDelay_mps*p.holdEfficiency_ppm/1000000);
  const setupSpent=ceilDiv(p.effectiveDelay_mps*p.setupCoupling_ppm,1000000);
  const hold=B.candidateHold_mps+recovered-p.holdAdverse_mps;
  const setup=B.candidateSetup_mps-setupSpent-p.setupAdverse_mps;
  const holdNeed=-B.candidateHold_mps+p.holdAdverse_mps;
  const setupBudget=B.candidateSetup_mps-B.setupGuard_mps-p.setupAdverse_mps;
  const minDelay=p.holdEfficiency_ppm===0?null:ceilDiv(holdNeed*1000000,p.holdEfficiency_ppm);
  const maxDelay=setupBudget<0?-1:p.setupCoupling_ppm===0?null:Math.floor(setupBudget*1000000/p.setupCoupling_ppm);
  const timingWindow=minDelay!==null&&(maxDelay===null||minDelay<=maxDelay);
  const maxAreaAdded=Math.floor(16*B.serialArea_micro/18)-B.candidateArea_micro;
  return {scenario:p.name||"unnamed",effectiveDelay_mps:p.effectiveDelay_mps,holdSlack_mps:hold,setupSlack_mps:setup,holdPass:hold>=0,setupPass:setup>=B.setupGuard_mps,candidateTimingPass:hold>=0&&setup>=B.setupGuard_mps,minEffectiveDelay_mps:minDelay,maxEffectiveDelay_mps:maxDelay,windowExists:timingWindow,packing18v16Pass:p.candidateAreaAdded_micro<=maxAreaAdded,packingAreaHeadroom_micro:maxAreaAdded-p.candidateAreaAdded_micro,serialRequiredSetupRecovery_mps:B.setupGuard_mps-B.serialSetup_mps,serialRequiredHoldRecovery_mps:-B.serialHold_mps};
}
function selfTest(){
  const cases=[
    {name:"predicted_local_win",effectiveDelay_mps:25000,holdEfficiency_ppm:1000000,setupCoupling_ppm:250000,holdAdverse_mps:0,setupAdverse_mps:2000,candidateAreaAdded_micro:300000000,expect:true},
    {name:"predicted_shared_setup_loss",effectiveDelay_mps:25000,holdEfficiency_ppm:1000000,setupCoupling_ppm:1200000,holdAdverse_mps:0,setupAdverse_mps:0,candidateAreaAdded_micro:300000000,expect:false},
    {name:"predicted_low_hold_transfer",effectiveDelay_mps:25000,holdEfficiency_ppm:450000,setupCoupling_ppm:250000,holdAdverse_mps:0,setupAdverse_mps:0,candidateAreaAdded_micro:300000000,expect:false},
    {name:"predicted_route_headwind",effectiveDelay_mps:25000,holdEfficiency_ppm:750000,setupCoupling_ppm:800000,holdAdverse_mps:3000,setupAdverse_mps:6000,candidateAreaAdded_micro:700000000,expect:false}
  ];
  const results=cases.map(c=>{const r=analyze(c);if(r.candidateTimingPass!==c.expect)throw Error("scenario regression "+c.name);return r});
  if(results[0].holdSlack_mps!==12378||results[0].setupSlack_mps!==65986)throw Error("local case arithmetic");
  if(results[1].setupSlack_mps!==44236||results[2].holdSlack_mps!==-1372||results[3].setupSlack_mps!==48236)throw Error("negative case arithmetic");
  if(results[0].packingAreaHeadroom_micro!==347354861)throw Error("packing arithmetic");
  if(results[0].serialRequiredSetupRecovery_mps!==801540)throw Error("serial guard arithmetic");
  for(const bad of [{...cases[0],holdEfficiency_ppm:1000001},{...cases[0],effectiveDelay_mps:-1}]){let rejected=false;try{analyze(bad)}catch(e){rejected=true}if(!rejected)throw Error("invalid input accepted")}
  return results;
}
if (require.main === module) {
  const rows = selfTest();
  const output = {evidence_tier:"CONDITIONAL_PRE_OUTCOME_SENSITIVITY_NOT_PHYSICAL",baseline:B,rows,
    caveats:["25 ps OpenROAD slack_margin is a repair TARGET, not an observed inserted path delay.",
      "Independent path and clock changes can invalidate the two-parameter transfer model.",
      "Electrical/DRC closure and serial-control feasibility are NOT inferred.",
      "Area packing excludes memory, interconnect, and integration overhead.",
      "Prospective real-workload holdouts remain sealed."]};
  process.stdout.write(JSON.stringify(output,null,2)+"\n");
}
module.exports = {analyze,selfTest};
