#!/usr/bin/env node
'use strict';
/* Adversarial rotating-priority serial baseline, preregistered before results. */
const {scenario,rescue}=require('./v297_bank_rescue.js');
const DEV=[3101,3119,3137,3167],HOLD=[4103,4127,4153,4177],CYCLES=100000;
const REGIMES=['motif_iid','uniform16','all_hot','single_issue','single_ready','bursty'];
function pop(a){return a.reduce((s,x)=>s+Number(x),0);}
function rotateGreedy(valid,pairs,B,t){const granted=[false,false,false],used=new Int8Array(16);let n=0;for(let step=0;step<3;step++){
 const i=(t%3+step)%3;if(!valid[i]||n===B)continue;
 const [a,b]=pairs[i];const fits=a===b?used[a]===0:used[a]<2&&used[b]<2;
 if(fits){granted[i]=true;used[a]++;used[b]++;n++;}
 }return granted;}
function runOne(regime,seed){let cooldown=false,priority=0,rotation=0,candidate=0;
 for(let t=0;t<CYCLES;t++){const {valid,pairs,B}=scenario(regime,seed,t);const v=rescue(valid,pairs,B,cooldown);cooldown=v.rescued;
 const f=rotateGreedy(valid,pairs,B,3*Math.floor(t/3)); // 0-1-2 baseline, independent serial implementation
 const r=rotateGreedy(valid,pairs,B,t);
 priority+=pop(f);rotation+=pop(r);candidate+=pop(v.grants);
 }return {seed,priority:priority/CYCLES,rotation:rotation/CYCLES,candidate:candidate/CYCLES};}
function mean(rows,k){return rows.reduce((s,r)=>s+r[k],0)/rows.length;}
function main(){const results=[];for(const regime of REGIMES){const dev=DEV.map(s=>runOne(regime,s)),hold=HOLD.map(s=>runOne(regime,s));results.push({regime,development:{fixed:mean(dev,'priority'),rotating:mean(dev,'rotation'),candidate:mean(dev,'candidate')},holdout:{fixed:mean(hold,'priority'),rotating:mean(hold,'rotation'),candidate:mean(hold,'candidate')},candidateMinusRotation:mean(hold,'candidate')-mean(hold,'rotation'),holdoutSeeds:HOLD});}
 return {evidenceTier:'SYNTHETIC_ADVERSARIAL_ROTATION_ONLY',prereg:'V297_ROTATING_CONTROL_PREREG_20261028.md',cyclesPerSeed:CYCLES,results,matchedPhysicalComparison:false};}
if(require.main===module)console.log(JSON.stringify(main(),null,2));
module.exports={rotateGreedy,runOne,main};
