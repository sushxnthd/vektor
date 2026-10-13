// Independent exact selector feasibility check: 16 banks, 3 queued requests.
#include <cassert>
#include <iostream>
#include <vector>
int main(){
 long n=0,strict=0,equal=0;
 for(int a=0;a<16;a++)for(int b=0;b<16;b++)for(int c=0;c<16;c++){
  std::vector<int> v={a,b,c};
  int flexible=1,fixed=1;
  for(int i=0;i<3;i++)for(int j=i+1;j<3;j++){
    if(v[i]!=v[j])flexible=2;
    if((v[i]&1)!=(v[j]&1))fixed=2;
  }
  assert(flexible>=fixed);
  strict+=(flexible>fixed);equal+=(flexible==fixed);++n;
 }
 assert(n==4096 && strict==1008 && equal==3088);
 std::cout<<"V145 PASS: "<<n<<" bank tuples; strict="<<strict<<" equal="<<equal<<"\n";
}
