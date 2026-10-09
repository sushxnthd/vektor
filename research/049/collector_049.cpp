// Vektor-049: deterministic scoreboard + RF return-bandwidth model.
// Research simulator; NOT RTL, silicon, or a calibrated GPU performance model.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int O=3, MAXB=16;
uint32_t mix32(uint32_t x){x^=x>>16;x*=0x7feb352dU;x^=x>>15;x*=0x846ca68bU;return x^(x>>16);}
uint32_t source_value(int w,int seq,int op){return mix32(0x490049U ^ uint32_t(w*65537u) ^ uint32_t(seq*131071u) ^ uint32_t(op*8191u));}
uint32_t result_value(int w,int seq){return mix32(0x04905090U ^ uint32_t(w*2654435761u) ^ uint32_t(seq*2246822519u));}
struct Instr{array<int,O> bank{};array<uint32_t,O> val{};int seq=0,born=0;bool dependent=false;};
struct Wave{Instr ins;array<int,O> state{};array<uint32_t,O> data{};int next_seq=0, ready_at=0;uint32_t producer_value=0;int last_issue=-1;};
struct Response{int wave,seq,op,bank,due;uint32_t value;uint64_t ticket;};
struct Config{int W=32,B=16,L=8,R=4,Q=64,D=50,policy=0,ret_policy=0,pattern=0,cycles=1200,warm=200;uint32_t seed=0x4901;};
struct Metrics{int issues=0,reads=0,returns=0,bad=0,bank_overflows=0,queue_overflows=0,stale=0,return_block_cycles=0,queue_block_cycles=0,dep_block_cycles=0,bank_block=0,max_outstanding=0,max_matured=0;double ipc=0,jain=0,mean_latency=0;int min_issue=0,max_issue=0;uint64_t checksum=1469598103934665603ull;};
Instr make_instr(int w,int seq,int t,int B,int D,int pattern,uint32_t seed,uint32_t prev){
 Instr a;a.seq=seq;a.born=t;
 a.dependent=(seq>0 && int(mix32(seed ^ uint32_t(w*8191u) ^ uint32_t(seq*65537u))%100u)<D);
 for(int o=0;o<O;o++){
  uint32_t h=mix32(seed ^ uint32_t(w*0x9e3779b9u) ^ uint32_t(seq*0x85ebca6bu) ^ uint32_t(o*0xc2b2ae35u));
  if(pattern==1)a.bank[o]=0;
  else if(pattern==2)a.bank[o]=(w+seq+o)%B;
  else a.bank[o]=int(h%uint32_t(B));
  a.val[o]=(o==0 && a.dependent)?prev:source_value(w,seq,o);
 }
 return a;
}
Metrics simulate(const Config& c){
 if(c.W<1||c.W>64||c.B<1||c.B>MAXB||c.R<1||c.Q<1||c.L<1||c.cycles<=c.warm)throw runtime_error("bad config");
 vector<Wave> waves(c.W);vector<Response> flight;flight.reserve(c.Q+O*c.W);
 for(int w=0;w<c.W;w++)waves[w].ins=make_instr(w,0,0,c.B,c.D,c.pattern,c.seed,0);
 vector<int> counts(c.W);Metrics m;uint64_t ticket=0;long long sumlat=0;
 auto phase_at=[&](int t){return c.policy==2?(t+t/9)%c.W:t%c.W;};
 for(int t=0;t<c.cycles;t++){
  // Matured response arbitration; unreturned responses retain identity and backpressure Q.
  vector<int> mature;for(int i=0;i<int(flight.size());i++)if(flight[i].due<=t)mature.push_back(i);
  m.max_matured=max(m.max_matured,int(mature.size()));
  if(int(mature.size())>c.R)m.return_block_cycles++;
  if(c.ret_policy==1){ // completion-aware return: favor wave with most already returned operands
   stable_sort(mature.begin(),mature.end(),[&](int a,int b){
    auto& x=waves[flight[a].wave];auto& y=waves[flight[b].wave];
    int cx=count(x.state.begin(),x.state.end(),2),cy=count(y.state.begin(),y.state.end(),2);
    return cx>cy;
   });
  }
  vector<unsigned char> deliver(flight.size(),0);
  for(int k=0;k<min(c.R,int(mature.size()));k++){
   int idx=mature[k];deliver[idx]=1;const auto& r=flight[idx];Wave& w=waves[r.wave];
   if(w.ins.seq!=r.seq || w.state[r.op]!=1){m.stale++;continue;}
   w.state[r.op]=2;w.data[r.op]=r.value;m.returns++;
  }
  vector<Response> remaining;remaining.reserve(flight.size());
  for(int i=0;i<int(flight.size());i++)if(!deliver[i])remaining.push_back(flight[i]);
  flight.swap(remaining);
  // Execute up to four fully collected instructions; scoreboard prohibits RAW early issue.
  int phase=phase_at(t);int issued_now=0;
  for(int k=0;k<c.W;k++){
   int w=(phase+k)%c.W;Wave& q=waves[w];
   if(!all_of(q.state.begin(),q.state.end(),[](int x){return x==2;}))continue;
   if(q.ins.dependent && t<q.ready_at){m.dep_block_cycles++;continue;}
   if(issued_now==4)break;
   for(int o=0;o<O;o++)if(q.data[o]!=q.ins.val[o])m.bad++;
   uint32_t output=result_value(w,q.ins.seq);
   m.checksum^=uint64_t(output)^uint64_t((w+1)*131071u)^uint64_t(q.ins.seq);m.checksum*=1099511628211ull;
   if(t>=c.warm){counts[w]++;m.issues++;sumlat+=t-q.ins.born;}
   issued_now++;q.last_issue=t;q.ready_at=t+4;q.producer_value=output;
   q.next_seq++;q.ins=make_instr(w,q.next_seq,t,c.B,c.D,c.pattern,c.seed,output);
   q.state={0,0,0};q.data={0,0,0};
  }
  // Schedule operand reads, bounded by per-bank read ports and total outstanding slots.
  vector<int> order(c.W);iota(order.begin(),order.end(),0);
  if(c.policy==1){stable_sort(order.begin(),order.end(),[&](int a,int b){
    int ca=count(waves[a].state.begin(),waves[a].state.end(),2);
    int cb=count(waves[b].state.begin(),waves[b].state.end(),2);
    if(ca!=cb)return ca>cb;
    return (a-phase+c.W)%c.W<(b-phase+c.W)%c.W;
  });}else stable_sort(order.begin(),order.end(),[&](int a,int b){return (a-phase+c.W)%c.W<(b-phase+c.W)%c.W;});
  array<int,MAXB> bank_used{};
  for(int w:order)for(int o=0;o<O;o++){
   Wave& q=waves[w];if(q.state[o]!=0)continue;
   if(o==0 && q.ins.dependent && t<q.ready_at){m.dep_block_cycles++;continue;}
   int b=q.ins.bank[o];
   if(bank_used[b]>=2){m.bank_block++;continue;}
   if(int(flight.size())>=c.Q){m.queue_block_cycles++;continue;}
   bank_used[b]++;q.state[o]=1;
   flight.push_back({w,q.ins.seq,o,b,t+c.L,q.ins.val[o],ticket++});m.reads++;
  }
  for(int b=0;b<c.B;b++)if(bank_used[b]>2)m.bank_overflows++;
  if(int(flight.size())>c.Q)m.queue_overflows++;
  m.max_outstanding=max(m.max_outstanding,int(flight.size()));
 }
 double sq=0;int n=0;for(int x:counts){n+=x;sq+=double(x)*x;}
 m.ipc=double(m.issues)/(c.cycles-c.warm);
 m.jain=sq?double(n)*n/(c.W*sq):0;
 m.min_issue=*min_element(counts.begin(),counts.end());m.max_issue=*max_element(counts.begin(),counts.end());
 m.mean_latency=m.issues?double(sumlat)/m.issues:0;
 if(m.bad||m.bank_overflows||m.queue_overflows||m.stale)throw runtime_error("safety invariant failed");
 if(m.reads-m.returns!=int(flight.size()))throw runtime_error("response conservation failed");
 return m;
}
int main(int argc,char**argv){
 if(argc>1 && string(argv[1])=="single"){
  if(argc!=14){cerr<<"usage: single W B L R Q D policy ret_policy pattern cycles warm seed\n";return 2;}
  Config c;c.W=atoi(argv[2]);c.B=atoi(argv[3]);c.L=atoi(argv[4]);c.R=atoi(argv[5]);c.Q=atoi(argv[6]);c.D=atoi(argv[7]);c.policy=atoi(argv[8]);c.ret_policy=atoi(argv[9]);c.pattern=atoi(argv[10]);c.cycles=atoi(argv[11]);c.warm=atoi(argv[12]);c.seed=uint32_t(strtoul(argv[13],nullptr,0));
  auto m=simulate(c);cout<<m.issues<<","<<m.reads<<","<<m.returns<<","<<m.bad<<","<<m.stale<<","<<m.bank_overflows<<","<<m.queue_overflows<<","<<m.checksum<<"\n";return 0;
 }
 if(argc>1 && string(argv[1])=="return"){
  cout<<"B,L,R,Q,D,seed,pattern,ret_policy,ipc,jain,mean_latency,min_issue,max_issue,return_block_cycles,max_matured,checksum\n";
  Config c;for(int B:{4,16})for(int L:{2,8})for(int R:{2,4})for(int Q:{8,64})for(int D:{0,50,100})for(int j=0;j<8;j++)for(int rp:{0,1}){
   c.B=B;c.L=L;c.R=R;c.Q=Q;c.D=D;c.policy=0;c.ret_policy=rp;c.pattern=j==7?2:0;
   c.seed=mix32(0x049C5090u+uint32_t(j*17+B*103+L*809+R*1187+Q*3329+D*7193));
   auto m=simulate(c);
   cout<<B<<","<<L<<","<<R<<","<<Q<<","<<D<<","<<j<<","<<c.pattern<<","<<rp<<","<<setprecision(8)<<m.ipc<<","<<m.jain<<","<<m.mean_latency<<","<<m.min_issue<<","<<m.max_issue<<","<<m.return_block_cycles<<","<<m.max_matured<<","<<m.checksum<<"\n";
  }
  return 0;
 }
 cout<<"B,L,R,Q,D,seed,pattern,policy,ipc,issues,reads,returns,jain,mean_latency,min_issue,max_issue,return_block_cycles,queue_block_cycles,dep_block_cycles,bank_block,max_outstanding,max_matured,bad,checksum\n";
 Config c;const uint32_t seed=0x04905090u;
 for(int B:{1,4,16})for(int L:{2,8})for(int R:{2,4,16})for(int Q:{8,64})for(int D:{0,50,100})for(int j=0;j<6;j++)for(int p:{0,1,2}){
  c.B=B;c.L=L;c.R=R;c.Q=Q;c.D=D;c.policy=p;c.ret_policy=0;c.seed=mix32(seed+uint32_t(j*17+B*103+L*809+D*7193+(argc>1 && string(argv[1])=="paired"?0:R*1187+Q*3329)));c.pattern=j==5?2:0;
  auto m=simulate(c);
  cout<<B<<","<<L<<","<<R<<","<<Q<<","<<D<<","<<j<<","<<c.pattern<<","<<p<<","<<setprecision(8)<<m.ipc<<","<<m.issues<<","<<m.reads<<","<<m.returns<<","<<m.jain<<","<<m.mean_latency<<","<<m.min_issue<<","<<m.max_issue<<","<<m.return_block_cycles<<","<<m.queue_block_cycles<<","<<m.dep_block_cycles<<","<<m.bank_block<<","<<m.max_outstanding<<","<<m.max_matured<<","<<m.bad<<","<<m.checksum<<"\n";
 }
}
