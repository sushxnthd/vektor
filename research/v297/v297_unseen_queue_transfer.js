#!/usr/bin/env node
'use strict';
// Preregistered at V297_UNSEEN_QUEUE_TRANSFER_KILL_PREREG_20261029.md.
// Do not tune the policy or generator after opening these holdout regimes.
const {runOne} = require('./v297_persistent_queue.js');
const seeds=[17401,17417,17431,17443];
const regimes=[
  ['motif3_burst37',3],
  ['uniform16',3],
  ['hot',1],
  ['motif3_burst37',1],
  ['hot',3]
];
const rows=[];
for(const [regime,rate] of regimes){
  const observations={};
  for(const policy of ['v297','oracle']){
    const xs=seeds.map(seed=>runOne(regime,rate,seed,policy));
    const metrics=['throughput','drops','p99Latency','meanLatency','maxOldestAge','maxBacklog','readsPerCycle','portViolations'];
    observations[policy]=Object.fromEntries(metrics.map(k=>[k,xs.reduce((sum,x)=>sum+x[k],0)/xs.length]));
  }
  const c=observations.v297, m=observations.oracle;
  rows.push({
    regime, arrivalsPerCycle:rate, observations,
    maxpairNoWorse: m.throughput+0.0001>=c.throughput && m.drops<=c.drops+3,
    deltaThroughput: m.throughput-c.throughput,
    deltaDrops: m.drops-c.drops
  });
}
const result={
  evidenceTier:'PROSPECTIVE_UNSEEN_SYNTHETIC_QUEUE_TRANSFER',
  originalGeneratorBlobSha:'7e85e328c6d6d1b79ab7082a8ab0171cdb442657',
  prereg:'V297_UNSEEN_QUEUE_TRANSFER_KILL_PREREG_20261029.md',
  seeds, warmup:1000, measuredCyclesPerSeed:20000, capacity:64,
  rows, allMaxpairNoWorse:rows.every(r=>r.maxpairNoWorse)
};
if(rows.some(r=>r.observations.v297.portViolations||r.observations.oracle.portViolations))throw Error('Bank port violation');
console.log(JSON.stringify(result,null,2));
