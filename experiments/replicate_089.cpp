// Vektor-089 independent C++17 event simulator; checks Python-generated per-cycle trace.
#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <string>
#include <sstream>
using namespace std;
struct Event {int uid,tag;};
struct Machine {
 int bits,bound,mode,t=0,next=0,uid=0,active_uid=-1,active_tag=-1;
 vector<int> until;
 map<int,vector<Event>> pending;
 long long bad=0,correct=0,stale=0,stall=0,admitted=0,canceled=0,idle=0,violations=0;
 Machine(int b,int d,int m):bits(b),bound(d),mode(m),until(1<<b,-1){}
 void tick(int offer,int cancel,int delay) {
  auto it=pending.find(t);
  if(it!=pending.end()){
   for(auto e:it->second){
    if(active_uid>=0 && e.tag==active_tag){
     if(e.uid==active_uid)correct++; else bad++;
     active_uid=-1;active_tag=-1;
    } else stale++;
   }
   pending.erase(it);
  }
  if(cancel && active_uid>=0){active_uid=-1;active_tag=-1;canceled++;}
  if(offer && active_uid<0){
   int tag=-1,n=1<<bits;
   if(mode==2)tag=uid;
   else if(mode==0){tag=next;next=(next+1)%n;}
   else for(int j=0;j<n;j++){int k=(next+j)%n;if((mode==3)?(t>=until[k]):(t>until[k])){tag=k;next=(k+1)%n;break;}}
   if(tag<0)stall++;
   else {
    active_uid=uid++;active_tag=tag;admitted++;
    pending[t+delay].push_back({active_uid,tag});
    if(mode==1 || mode==3)until[tag]=t+bound;
    if(delay>bound)violations++;
   }
  }
  if(active_uid<0)idle++;
  t++;
 }
};
int main(int argc,char**argv){
 if(argc!=2){cerr<<"usage: replicate_089 <trace.csv>\n";return 2;}
 ifstream f(argv[1]);if(!f){cerr<<"cannot open trace\n";return 2;}
 string line;getline(f,line);int checks=0;
 while(getline(f,line)){
  if(line.empty())continue;
  stringstream ss(line);vector<long long> v;string cell;
  while(getline(ss,cell,','))v.push_back(stoll(cell));
  if(v.size()!=15){cerr<<"bad row "<<v.size()<<"\n";return 2;}
  static Machine* m[4]={nullptr,nullptr,nullptr,nullptr};
  if(v[0]==0 && v[3]==0){for(int p=0;p<4;p++){delete m[p];m[p]=new Machine(v[1],v[2],p);}}
  int p=v[3];m[p]->tick(v[4],v[5],v[6]);
  long long got[]={m[p]->bad,m[p]->correct,m[p]->stale,m[p]->stall,m[p]->admitted,m[p]->canceled,m[p]->idle,m[p]->violations};
  for(int k=0;k<8;k++){
   if(got[k]!=v[7+k]){cerr<<"mismatch row="<<checks<<" metric="<<k<<" got="<<got[k]<<" expected="<<v[7+k]<<"\n";return 1;}
   checks++;
  }
 }
 cout<<"PASS "<<checks<<" independent C++/Python per-cycle metric comparisons\n";
}
