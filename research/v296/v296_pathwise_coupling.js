#!/usr/bin/env node
"use strict";
/* V296 pathwise closed-loop admission equivalence under bursty workload traces.
 * Predeclared regimes: V296_PATHWISE_COUPLING_PREREG_20261028.md
 * Synthetic falsification only; NOT RTL signoff, GPU speedup or physical power.
 */
const FROZEN=[
  {
    "name": "uniform_high_ready",
    "B": 4,
    "L": 1,
    "q": 0.96,
    "hot": 0,
    "same": 0.08,
    "burst": false
  },
  {
    "name": "hotspot_same_bank",
    "B": 4,
    "L": 1,
    "q": 0.98,
    "hot": 0.94,
    "same": 0.92,
    "burst": false
  },
  {
    "name": "shared_port_bottleneck",
    "B": 1,
    "L": 2,
    "q": 0.94,
    "hot": 0.15,
    "same": 0.15,
    "burst": false
  },
  {
    "name": "low_occupancy",
    "B": 4,
    "L": 5,
    "q": 0.22,
    "hot": 0.25,
    "same": 0.4,
    "burst": false
  },
  {
    "name": "temporal_bursts",
    "B": 2,
    "L": 3,
    "q": 0.85,
    "hot": 0.9,
    "same": 0.5,
    "burst": true
  }
];
const SEEDS=[1701,1709,1723,1741];
function assert(x,msg){if(!x)throw Error(msg||"assertion failed");}

function h(seed,cycle,w,salt){let x=(seed^Math.imul(cycle+1,0x9e3779b1)^Math.imul(w+17,0x85ebca6b)^Math.imul(salt+31,0xc2b2ae35))>>>0;x^=x>>>16;x=Math.imul(x,0x7feb352d);x^=x>>>15;x=Math.imul(x,0x846ca68b);x^=x>>>16;return x>>>0;}

function u(seed,cycle,w,salt){return h(seed,cycle,w,salt)/4294967296;}

function banks(seed,cycle,w,sc){let hot=sc.burst?(Math.floor(cycle/37)%2?sc.hot:0.03):sc.hot;let a=u(seed,cycle,w,2)<hot?0:Math.floor(16*u(seed,cycle,w,3));let b=u(seed,cycle,w,4)<sc.same?a:(u(seed,cycle,w,5)<hot?0:Math.floor(16*u(seed,cycle,w,6)));return [a,b];}

function serial(valid,pairs){let once=0,twice=0,out=[];for(let i=0;i<pairs.length;i++){let [a,b]=pairs[i],ma=1<<a,mb=1<<b;let ok=!!valid[i]&&(a===b?!(once&ma):!(twice&ma)&&!(twice&mb));out.push(ok);if(ok){if(a===b){once|=ma;twice|=ma;}else{twice|=once&(ma|mb);once|=ma|mb;}}}return out;}

function pairwise(valid,pairs){let out=[];for(let i=0;i<pairs.length;i++){let [a,b]=pairs[i],ca=0,cb=0;for(let j=0;j<i;j++)if(out[j]){let [x,y]=pairs[j];ca+=(a===x)+(a===y);cb+=(b===x)+(b===y);}out.push(!!valid[i]&&(a===b?ca===0:ca<2&&cb<2));}return out;}

function mutant(valid,pairs){let out=pairwise(valid,pairs);for(let i=0;i<pairs.length;i++)if(valid[i]&&pairs[i][0]===pairs[i][1])out[i]=true;return out;}

function portSafe(grants,pairs){let count=new Array(16).fill(0);for(let i=0;i<grants.length;i++)if(grants[i]){count[pairs[i][0]]++;count[pairs[i][1]]++;}return count.every(x=>x<=2);}

function simulate(mode,sc,seed,cycles=5000){let ready=new Array(32).fill(0),cursor=0,accepted=0,traffic=0,collision=0,compatible=0,overlap=0,paired=0,portViolations=0,trace=[];let arb=mode==="serial"?serial:mode==="mutant"?mutant:pairwise;for(let t=0;t<cycles;t++){let q=sc.burst?(Math.floor(t/53)%2?sc.q:0.16):sc.q;let waves=[];for(let j=0;j<32&&waves.length<4;j++){let w=(cursor+j)%32;if(ready[w]<=t&&u(seed,t,w,1)<q)waves.push(w);}let bp=waves.map(w=>banks(seed,t,w,sc));if(bp.length>=2){paired++;let a=new Set(bp[0]),b=new Set(bp[1]);let common=0;for(let v of a)if(b.has(v))common++;overlap+=common>0?1:0;compatible+=common===0?1:0;}let grant=arb(waves.map(()=>true),bp);if(!portSafe(grant,bp))portViolations++;let issued=[];for(let j=0;j<grant.length;j++)if(grant[j]&&issued.length<sc.B)issued.push(waves[j]);collision+=grant.filter(x=>!x).length;for(let w of issued){ready[w]=t+sc.L;cursor=(w+1)%32;}accepted+=issued.length;traffic+=2*issued.length;trace.push(issued.join(","));}return {accepted,traffic,collision,portViolations,compatibilityRate:paired?compatible/paired:null,overlapRate:paired?overlap/paired:null,trace};}

function exhaustive(){let count=0;for(let mask=0;mask<16;mask++){let valid=Array.from({length:4},(_,i)=>!!(mask&(1<<i)));for(let code=0;code<6561;code++){let n=code,pairs=[];for(let i=0;i<4;i++){let a=n%3;n=Math.floor(n/3);let b=n%3;n=Math.floor(n/3);pairs.push([a,b]);}let a=serial(valid,pairs),b=pairwise(valid,pairs);assert(a.every((v,i)=>v===b[i]),"canonical admission mismatch");assert(portSafe(a,pairs),"two-port violation");count++;}}assert(count===104976,"exhaustive count");return count;}

function main(){let exhaustiveCases=exhaustive(),rows=[];for(let sc of FROZEN){let examples=[];for(let seed of SEEDS){let a=simulate("pairwise",sc,seed),b=simulate("serial",sc,seed);assert(a.trace.length===b.trace.length,"trace length");for(let t=0;t<a.trace.length;t++)assert(a.trace[t]===b.trace[t],sc.name+" seed "+seed+" cycle "+t);assert(a.accepted===b.accepted&&a.traffic===b.traffic&&a.collision===b.collision,"aggregate mismatch");assert(a.portViolations===0&&b.portViolations===0,"two-port safety");examples.push({seed,waves:a.accepted,operandReads:a.traffic,collisionRejections:a.collision,compatibilityRate:a.compatibilityRate,overlapRate:a.overlapRate,exactTraceEqual:true});}rows.push({name:sc.name,B:sc.B,L:sc.L,readiness:sc.q,hot:sc.hot,sameBankOperand:sc.same,examples});}let mut=simulate("mutant",FROZEN[1],SEEDS[0],200),ref=simulate("serial",FROZEN[1],SEEDS[0],200);assert(mut.trace.some((v,i)=>v!==ref.trace[i]),"mutant escaped");return {evidenceTier:"SYNTHETIC_PATHWISE_COUPLING_NOT_PHYSICAL_OR_GPU",prereg:"V296_PATHWISE_COUPLING_PREREG_20261028.md",canonicalCases:exhaustiveCases,scenarios:rows,mutantDetected:true,matchedClockAndLatencyGain:0,physicalPowerEstablished:false,matchedPhysicalFeasibilityEstablished:false};}
if (require.main === module) {
 const result=main();
 if (process.argv.includes("--self-test")) {
  process.stdout.write("V296_PATHWISE_COUPLING_SELFTEST_PASS "+result.canonicalCases+"\n");
 } else {
  process.stdout.write(JSON.stringify(result,null,2)+"\n");
 }
}
