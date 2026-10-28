#!/usr/bin/env node
'use strict';
/* Independent exhaustive small-bank semantic audit; no RTL import. */
function fits(a,b){const v=[a[0],a[1],b[0],b[1]];return !((v[0]===v[1]&&v[0]===v[2])||(v[0]===v[1]&&v[0]===v[3])||(v[0]===v[2]&&v[0]===v[3])||(v[1]===v[2]&&v[1]===v[3]));}
function greedy(valid,pairs){const g=[0,0,0];for(let i=0;i<3;i++){if(!(valid&(1<<i)))continue;const selected=g.findIndex(Boolean);if(selected<0||g.reduce((s,v)=>s+v,0)<2&&fits(pairs[selected],pairs[i]))g[i]=1;}return g.reduce((m,v,i)=>m|(v<<i),0);}
function maxpair(valid,pairs){for(const [i,j] of [[0,1],[0,2],[1,2]])if((valid&(1<<i))&&(valid&(1<<j))&&fits(pairs[i],pairs[j]))return (1<<i)|(1<<j);for(let i=0;i<3;i++)if(valid&(1<<i))return 1<<i;return 0;}
function compact(valid,pairs,cool){const p01=(valid&3)===3&&fits(pairs[0],pairs[1]);const p02=(valid&5)===5&&fits(pairs[0],pairs[2]);const p12=(valid&6)===6&&fits(pairs[1],pairs[2]);return p01?3:p02?5:p12?((valid&1)&&cool?1:6):(valid&1)?1:(valid&2)?2:(valid&4)?4:0;}
function candidate(valid,pairs,cool){const base=greedy(valid,pairs);const motif=(base===1||base===2||base===4)&&(valid&6)===6&&fits(pairs[1],pairs[2]);return !cool&&motif?6:base;}
function count(x){return (x&1)+((x>>1)&1)+((x>>2)&1);}
function main(){let n=0,mismatches=0,domination=0,strict=0,strictWithoutCooldown=0;for(let valid=0;valid<8;valid++)for(let code=0;code<729;code++){let x=code,pairs=[];for(let i=0;i<3;i++){const a=x%3;x=Math.floor(x/3);const b=x%3;x=Math.floor(x/3);pairs.push([a,b]);}for(let cool=0;cool<2;cool++){const a=candidate(valid,pairs,cool),b=compact(valid,pairs,cool),o=maxpair(valid,pairs);n++;if(a!==b)mismatches++;if(count(o)<count(a))domination++;if(count(o)>count(a)){strict++;if(!cool)strictWithoutCooldown++;}}}if(mismatches||domination||strictWithoutCooldown)throw Error("dominance/equivalence failure");return {evidenceTier:"EXHAUSTIVE_SMALL_BANK_SEMANTIC_FALSIFICATION",canonicalCases:n,compactMismatches:mismatches,maxpairWorseCases:domination,maxpairStrictlyBetterCases:strict,strictWithoutCooldown,claim:"V297 grants are exactly a cooldown-constrained maximum-feasible-pair selector on all 3-bank canonical patterns; unrestricted max-pair never admits fewer on the same request vector."};}
if(require.main===module)console.log(JSON.stringify(main(),null,2));
module.exports={main};
