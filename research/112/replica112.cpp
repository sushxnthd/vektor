// Independent two-event SC legality oracle. Does not import V111 or Python.
#include <iostream>
#include <tuple>
#include <vector>
#include <cstdint>
using namespace std;
struct E {uint64_t cid,cta,wid,tid,pc,epoch,addr,size;char op,space;};
static bool check(const E&a,const E&b,const vector<vector<int>>&waves){
 if(waves.empty())return false;
 int p[2]={-1,-1};
 for(int k=0;k<(int)waves.size();k++){
  if(waves[k].empty()||waves[k].size()>32)return false;
  for(int i:waves[k]){if(i<0||i>1||p[i]>=0)return false;p[i]=k;}
  if(waves[k].size()==2){
   if(tie(a.cid,a.cta,a.pc,a.epoch,a.op,a.space,a.size)!=
      tie(b.cid,b.cta,b.pc,b.epoch,b.op,b.space,b.size))return false;
   if(tie(a.cid,a.cta,a.wid,a.tid)==tie(b.cid,b.cta,b.wid,b.tid))return false;
  }
 }
 if(p[0]<0||p[1]<0)return false;
 auto valid=[](const E&e){return e.size==1||e.size==2||e.size==4||e.size==8||e.size==16;};
 if(!valid(a)||!valid(b)||a.addr>UINT64_MAX-a.size+1||b.addr>UINT64_MAX-b.size+1)return false;
 if(a.op!='L'&&a.op!='S'&&a.op!='A')return false;
 if(b.op!='L'&&b.op!='S'&&b.op!='A')return false;
 if(a.space!='G'&&a.space!='S'&&a.space!='L')return false;
 if(b.space!='G'&&b.space!='S'&&b.space!='L')return false;
 bool same_thread=tie(a.cid,a.cta,a.wid,a.tid)==tie(b.cid,b.cta,b.wid,b.tid);
 if(same_thread&&p[0]>=p[1])return false;
 bool same_cta=tie(a.cid,a.cta)==tie(b.cid,b.cta);
 if(same_cta&&a.epoch!=b.epoch){
  if(a.epoch<b.epoch&&p[0]>=p[1])return false;
  if(b.epoch<a.epoch&&p[1]>=p[0])return false;
 }
 bool same_instance=a.space==b.space&&(a.space=='G'||(a.space=='S'&&same_cta)||(a.space=='L'&&same_thread));
 bool overlap=(__uint128_t)a.addr<(__uint128_t)b.addr+b.size&&(__uint128_t)b.addr<(__uint128_t)a.addr+a.size;
 if(same_instance&&overlap&&(a.op!='L'||b.op!='L')&&p[0]>=p[1])return false;
 return true;
}
int main(){
 ios::sync_with_stdio(false);cin.tie(nullptr);int n;cin>>n;
 for(int c=0;c<n;c++){
  E e[2];for(auto&x:e)cin>>x.cid>>x.cta>>x.wid>>x.tid>>x.pc>>x.epoch>>x.op>>x.space>>x.addr>>x.size;
  int nw;cin>>nw;vector<vector<int>> w(nw);
  for(auto&v:w){int k;cin>>k;v.resize(k);for(int&i:v)cin>>i;}
  cout<<(check(e[0],e[1],w)?1:0)<<'\n';
 }
}
