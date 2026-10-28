#!/usr/bin/env node
'use strict';
/* V297 synthetic prospective test. Frozen in V297_BOUNDED_BANK_RESCUE_PREREG_20261028.md.
 * This is NOT GPU throughput, timing, area, or power evidence.
 */
const SEEDS_DEV=[1701,1709,1723,1741], SEEDS_HOLD=[2027,2039,2053,2063];
const CYCLES=100000;
const REGIMES=['motif_iid','uniform16','all_hot','single_issue','single_ready','bursty'];
function assert(v,msg){if(!v)throw Error(msg||'assert');}
function safe(mask,pairs,B=2){if(mask.reduce((s,x)=>s+Number(x),0)>B)return false;const count=new Array(16).fill(0);for(let i=0;i<3;i++)if(mask[i]){count[pairs[i][0]]++;count[pairs[i][1]]++;}return count.every(x=>x<=2);}
function greedy(valid,pairs,B=2){const out=[false,false,false];for(let i=0;i<3;i++){if(!valid[i])continue;out[i]=true;if(!safe(out,pairs,B))out[i]=false;}return out;}
function pop(a){return a.reduce((s,v)=>s+Number(v),0);}
function motif(valid,pairs,B){const base=greedy(valid,pairs,B);return B===2&&pop(base)===1&&valid[1]&&valid[2]&&safe([false,true,true],pairs,B);}
function rescue(valid,pairs,B=2,cooldown=false){const base=greedy(valid,pairs,B);if(!cooldown&&motif(valid,pairs,B))return {grants:[false,true,true],rescued:true};return {grants:base,rescued:false};}
function oracle(valid,pairs,B=2){let max=-1,mask=null;for(let m=0;m<8;m++){const bits=[0,1,2].map(i=>Boolean(m&(1<<i)));if(bits.some((v,i)=>v&&!valid[i])||!safe(bits,pairs,B))continue;const n=pop(bits);if(n>max){max=n;mask=bits;}}return {max,mask};}
function h(seed,t,salt){let x=(seed^Math.imul(t+1,0x9e3779b1)^Math.imul(salt+19,0x85ebca6b))>>>0;x^=x>>>16;x=Math.imul(x,0x7feb352d);x^=x>>>15;x=Math.imul(x,0x846ca68b);x^=x>>>16;return x>>>0;}
function u(seed,t,salt){return h(seed,t,salt)/4294967296;}
function scenario(regime,seed,t){let pairs,valid=[true,true,true],B=2;
 const isMotif=regime==='motif_iid'?u(seed,t,0)<0.4:regime==='bursty'?(Math.floor(t/37)%2===0):regime==='single_issue';
 if(isMotif)pairs=[[0,0],[0,1],[0,2]];
 else if(regime==='all_hot')pairs=[[0,0],[0,0],[0,0]];
 else pairs=[0,1,2].map(i=>[Math.floor(u(seed,t,2*i+1)*16),Math.floor(u(seed,t,2*i+2)*16)]);
 if(regime==='single_issue')B=1;
 if(regime==='single_ready')valid=[true,false,false];
 return {pairs,valid,B};}
function exhaustive(){let n=0,mutantCaught=false;for(let validBits=0;validBits<8;validBits++)for(let code=0;code<729;code++){
 let v=code,pairs=[];for(let i=0;i<3;i++){let a=v%3;v=Math.floor(v/3);let b=v%3;v=Math.floor(v/3);pairs.push([a,b]);}
 const valid=[0,1,2].map(i=>Boolean(validBits&(1<<i)));
 for(const B of [1,2]){const base=greedy(valid,pairs,B),out=rescue(valid,pairs,B,false),opt=oracle(valid,pairs,B);
 assert(safe(base,pairs,B)&&safe(out.grants,pairs,B),'port violation');
 assert(out.grants.every((x,i)=>!x||valid[i]),'invalid grant');
 assert(pop(out.grants)===opt.max,'non-optimal rescue');
 assert(pop(rescue(valid,pairs,B,true).grants)===pop(base),'cooldown bypass');
 assert(pop(out.grants)-pop(base)===(motif(valid,pairs,B)?1:0),'motif law');
 if(B===2&&pop(base)===1&&valid[1]&&valid[2]&&!safe([false,true,true],pairs,B))mutantCaught=true;
 }n++;}
 assert(n===5832&&mutantCaught,'negative control not discriminating');
 // Explicit unsafe mutant: two double-reads from bank zero exceed two physical ports.
 assert(!safe([false,true,true],[[0,1],[0,0],[0,0]],2),'unsafe mutant escaped');
 return {canonicalCases:n,configurationsChecked:n*2,mutantDetected:mutantCaught};}
function simulate(regime,seed){let cooldown=false,baseTotal=0,actualTotal=0,motifs=0,rescues=0,portViolations=0,oracleTotal=0,cooldownCycles=0,invalid=0;
 for(let t=0;t<CYCLES;t++){const {valid,pairs,B}=scenario(regime,seed,t);const base=greedy(valid,pairs,B),candidate=rescue(valid,pairs,B,cooldown);const isM=motif(valid,pairs,B);
 motifs+=Number(isM);baseTotal+=pop(base);actualTotal+=pop(candidate.grants);oracleTotal+=oracle(valid,pairs,B).max;
 if(cooldown)cooldownCycles++;if(candidate.rescued)rescues++;
 if(!safe(candidate.grants,pairs,B))portViolations++;
 if(candidate.grants.some((v,i)=>v&&!valid[i]))invalid++;
 assert(pop(candidate.grants)-pop(base)===Number(candidate.rescued),'cycle gain mismatch');
 cooldown=candidate.rescued;
 }
 assert(portViolations===0&&invalid===0,'safety');
 return {seed,baseline:baseTotal/CYCLES,candidate:actualTotal/CYCLES,gain:rescues/CYCLES,p:motifs/CYCLES,rescues,cooldownCycles,oracle:oracleTotal/CYCLES,portViolations};}
function average(rows,k){return rows.reduce((s,r)=>s+r[k],0)/rows.length;}
function run(){const ex=exhaustive(),results=[];for(const name of REGIMES){const dev=SEEDS_DEV.map(s=>simulate(name,s)),hold=SEEDS_HOLD.map(s=>simulate(name,s));const p=average(dev,'p'),Eg=average(dev,'baseline'),pred=p/(1+p),actual=average(hold,'gain');const error=Math.abs(actual-pred);
 const row={regime:name,development:{p,baseline:Eg,observedGain:average(dev,'gain')},holdout:{p:average(hold,'p'),baseline:average(hold,'baseline'),gain:actual,oracle:average(hold,'oracle')},iidPredictedGain:pred,absolutePredictionError:error,withinFrozenTolerance:error<=0.005,breakEvenClockRatio:Eg/(Eg+pred),maxPortViolations:Math.max(...hold.map(x=>x.portViolations)),holdoutSeeds:SEEDS_HOLD};
 if(name!=='bursty')assert(row.withinFrozenTolerance,'prospective iid law failed '+name+': '+error);
 results.push(row);
 }
 return {evidenceTier:'SYNTHETIC_THREE_REQUEST_ADMISSION_ONLY',prereg:'V297_BOUNDED_BANK_RESCUE_PREREG_20261028.md',exhaustive:ex,cyclesPerSeed:CYCLES,results,rtlValidated:false,physicalTimingValidated:false,matchedAreaValidated:false,actualGpuThroughputValidated:false};}
if(require.main===module){const result=run();if(process.argv.includes('--self-test'))console.log('V297_BANK_RESCUE_SELFTEST_PASS '+result.exhaustive.canonicalCases+' '+result.results.length);else console.log(JSON.stringify(result,null,2));}
module.exports={safe,greedy,motif,rescue,oracle,scenario,exhaustive,simulate,run};
