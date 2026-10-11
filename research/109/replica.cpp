// Independent C++ cohort validator for Vektor-109; no Python model imports.
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <vector>
#include <tuple>
#include <string>
using namespace std;
struct Event { int tid,pc,epoch; char op; long long addr,val; };
int main(){
  ios::sync_with_stdio(false);cin.tie(nullptr);
  int tests; if(!(cin>>tests))return 1;
  for(int tc=0;tc<tests;++tc){
    int n,m,width;cin>>n>>m>>width;
    vector<Event> e(n);
    for(auto &x:e)cin>>x.tid>>x.pc>>x.epoch>>x.op>>x.addr>>x.val;
    vector<vector<int>> waves(m);
    for(auto &w:waves){int k;cin>>k;w.resize(k);for(int &i:w)cin>>i;}
    bool ok=n>0&&m>0&&width>0;
    vector<int> pos(n,-1);
    for(int t=0;t<m;++t){
      const auto &w=waves[t];
      if(w.empty()||(int)w.size()>width)ok=false;
      set<int> tids; tuple<int,char,int> signature; bool first=true;
      for(int i:w){
        if(i<0||i>=n){ok=false;continue;}
        if(pos[i]!=-1)ok=false;
        pos[i]=t;
        auto sig=make_tuple(e[i].pc,e[i].op,e[i].epoch);
        if(first){signature=sig;first=false;}else if(sig!=signature)ok=false;
        if(!tids.insert(e[i].tid).second)ok=false;
      }
    }
    if(any_of(pos.begin(),pos.end(),[](int x){return x<0;}))ok=false;
    map<int,int> last_tid;
    map<long long,int> last_write;
    map<long long,set<int>> readers;
    vector<set<int>> deps(n);
    for(int i=0;i<n;++i){
      auto &x=e[i];
      if(last_tid.count(x.tid))deps[i].insert(last_tid[x.tid]);
      last_tid[x.tid]=i;
      if(last_write.count(x.addr))deps[i].insert(last_write[x.addr]);
      if(x.op=='S'||x.op=='A'){
        for(int p:readers[x.addr])deps[i].insert(p);
        readers[x.addr].clear();last_write[x.addr]=i;
      }else readers[x.addr].insert(i);
    }
    for(int i=0;i<n;++i)for(int p:deps[i])
      if(pos[p]<0||pos[i]<0||pos[p]>=pos[i])ok=false;
    map<int,pair<int,int>> bounds;
    for(int i=0;i<n;++i){
      if(!bounds.count(e[i].epoch))bounds[e[i].epoch]={m,-1};
      auto &b=bounds[e[i].epoch];
      b.first=min(b.first,pos[i]);b.second=max(b.second,pos[i]);
    }
    int last=-1;
    for(auto &entry:bounds){
      if(entry.second.first<=last)ok=false;
      last=entry.second.second;
    }
    cout<<(ok?1:0)<<'\n';
  }
}
