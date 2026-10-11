// Independent C++ service-slot model for 256 fixed discovery configurations.
// Input: pattern length rf_ports migration_bw memory_stride locality
// Output: baseline unconditional heuristic oracle
#include <algorithm>
#include <array>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
using namespace std;
struct Lane { int warp,lane,path,address; };
struct Result { long long cost; int groups,migrated; };
int divup(int a,int b) {return (a+b-1)/b;}
int main() {
 string pattern,locality;int length,ports,bw,stride;
 while(cin>>pattern>>length>>ports>>bw>>stride>>locality) {
  vector<Lane> all;
  for(int w=0;w<8;w++)for(int l=0;l<32;l++) {
   int p=0;
   if(pattern=="balanced")p=l%2;
   if(pattern=="minority")p=(l==31);
   if(pattern=="four_path")p=l%4;
   int addr=(w*32+l)*4;
   if(locality=="path_striped")addr=(p*8*32+w*32+l)*4;
   all.push_back({w,l,p,addr});
  }
  auto calculate=[&](bool compact)->Result {
   map<pair<int,int>,vector<Lane>> buckets;
   for(const auto& x:all)buckets[{compact?0:x.warp,x.path}].push_back(x);
   long long service=0;int groups=0,migrated=0;
   for(auto &entry:buckets) {
    auto &v=entry.second;
    int chunk=compact?32:(int)v.size();
    for(int pos=0;pos<(int)v.size();pos+=chunk) {
     int stop=min(pos+chunk,(int)v.size());groups++;
     if(compact) {
      map<int,int> freq;
      for(int i=pos;i<stop;i++)freq[v[i].warp]++;
      int biggest=0;for(auto &kv:freq)biggest=max(biggest,kv.second);
      migrated+=stop-pos-biggest;
     }
     for(int inst=0;inst<length;inst++) {
      array<int,16> hist{};
      set<int> lines;
      for(int i=pos;i<stop;i++) {
       const Lane &x=v[i];
       int r0=(inst*7)%64,r1=(inst*11+3)%64;
       hist[(x.warp*13+x.lane*5+r0*3)%16]++;
       hist[(x.warp*13+x.lane*5+r1*3)%16]++;
       if(stride && inst%stride==0)lines.insert(x.address/128);
      }
      int rf=1;for(int n:hist)rf=max(rf,divup(n,ports));
      int mem=divup((int)lines.size(),2);
      service+=max(rf,mem);
     }
    }
   }
   return {service+(compact?4+divup(migrated,bw):0),groups,migrated};
  };
  auto b=calculate(false),d=calculate(true);
  int est=(b.groups-d.groups)*8;
  long long h=est>4+divup(d.migrated,bw)?d.cost:b.cost;
  cout<<b.cost<<' '<<d.cost<<' '<<h<<' '<<min(b.cost,d.cost)<<'\n';
 }
}
