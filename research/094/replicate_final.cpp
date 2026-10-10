// Independent C++17 synthetic return model, not GPU throughput.
#include <iostream>
#include <vector>
#include <deque>
#include <algorithm>
using namespace std;
struct Beat{int uid,tag,due,born;bool final;};
struct Owner{int uid=-1;bool live=false;};
int main(){
 int T,N,W,pol,guard;if(!(cin>>T>>N>>W>>pol>>guard))return 2;
 vector<Owner> active(N);vector<int> last(N,-100000000);
 int rr=0,uid=0;vector<Beat> scheduled;deque<Beat> q;
 long long admitted=0,stalls=0,correct=0,wrong=0,stale=0,ignored=0,maxq=0,maxage=0,delivered=0;
 for(int t=0;t<T;t++){
  int offer,lat,copies,spacing,cancel,reset,dup;
  cin>>offer>>lat>>copies>>spacing>>cancel>>reset>>dup;
  vector<Beat> remaining;
  for(auto &b:scheduled){if(b.due<=t)q.push_back(b);else remaining.push_back(b);}
  scheduled.swap(remaining);maxq=max(maxq,(long long)q.size());
  for(int j=0;j<W&&!q.empty();j++){
   Beat b=q.front();q.pop_front();delivered++;maxage=max(maxage,(long long)(t-b.born));
   if(pol==1&&!b.final){ignored++;continue;}
   Owner a=active[b.tag];
   if(a.uid==-1)stale++;
   else if(a.uid!=b.uid){wrong++;active[b.tag]={-1,false};last[b.tag]=t;}
   else{if(a.live&&!reset)correct++;else stale++;active[b.tag]={-1,false};last[b.tag]=t;}
  }
  if(reset){for(auto &a:active)if(a.uid!=-1)a.live=false;}
  else for(int s=0;s<N;s++)if((cancel>>s)&1)if(active[s].uid!=-1)active[s].live=false;
  if(offer&&!reset){
   bool granted=false;
   for(int off=0;off<N;off++){
    int s=(rr+off)%N;
    if(active[s].uid==-1&&t>last[s]+guard){
     int id=uid++;active[s]={id,true};rr=(s+1)%N;
     for(int j=0;j<copies;j++)scheduled.push_back({id,s,t+lat+j*spacing,t,j==copies-1});
     if(dup>=0)scheduled.push_back({id,s,t+lat+(copies-1)*spacing+dup,t,true});
     admitted++;granted=true;break;
    }
   }
   if(!granted)stalls++;
  }
 }
 cout<<admitted<<' '<<stalls<<' '<<correct<<' '<<wrong<<' '<<stale<<' '<<ignored<<' '<<maxq<<' '<<maxage<<' '<<delivered<<'\n';
}
