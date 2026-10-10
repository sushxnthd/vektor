// Independent C++17 absolute-event calendar for Vektor-087 vectors.
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
int bits(int n) {int w=0;do {++w;n>>=1;}while(n);return w;}
struct Calendar {
 int banks,reqs,maxlat,ports,t=0;
 map<pair<int,int>,int> event;
 vector<int> ptr;
 Calendar(int b,int r,int l,int p):banks(b),reqs(r),maxlat(l),ports(p),ptr(b*(l+1),0){}
 pair<unsigned long long,unsigned long long> step(bool reset,unsigned long long valid,unsigned long long bs,unsigned long long ls){
  int bw=bits(banks-1),lw=bits(maxlat),cw=bits(ports);
  unsigned long long g=0,d=0;
  if(reset){event.clear();fill(ptr.begin(),ptr.end(),0);}
  else {
   for(int b=0;b<banks;b++)d|=(unsigned long long)event[{t,b}]<<(b*cw);
   for(int b=0;b<banks;b++)for(int l=1;l<=maxlat;l++){
    int &p=ptr[b*(maxlat+1)+l],start=p,last=-1;
    for(int off=0;off<reqs;off++){
     int i=(start+off)%reqs;
     int ib=(bs>>(i*bw))&((1<<bw)-1);
     int il=(ls>>(i*lw))&((1<<lw)-1);
     if((valid>>i&1)&&ib==b&&il==l&&event[{t+l,b}]<ports){
      ++event[{t+l,b}];g|=1ULL<<i;last=i;
     }
    }
    if(last>=0)p=(last+1)%reqs;
   }
  }
  ++t;return {g,d};
 }
};
int main(int argc,char**argv){
 if(argc!=6)throw runtime_error("usage: replicate_087 trace banks reqs max_latency ports");
 Calendar c(stoi(argv[2]),stoi(argv[3]),stoi(argv[4]),stoi(argv[5]));
 ifstream f(argv[1]);if(!f)throw runtime_error("missing vectors");
 string rst,v,b,l,g,d;int n=0;
 while(f>>rst>>v>>b>>l>>g>>d){
  auto got=c.step(rst=="0",stoull(v,nullptr,16),stoull(b,nullptr,16),stoull(l,nullptr,16));
  if(got.first!=stoull(g,nullptr,16)||got.second!=stoull(d,nullptr,16)){
   cerr<<"Mismatch at cycle "<<n<<"\n";return 1;
  }
  ++n;
 }
 cout<<"PASS independent C++: "<<n<<" cycles, "<<2*n<<" comparisons\n";
}
