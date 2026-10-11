// V097 independent C++17 vector replay, separate from Python golden model.
#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
int main(int argc,char**argv){
 if(argc!=4){cerr<<"usage: replicate FILE SOURCES GUARD\n";return 2;}
 int n=stoi(argv[2]),guard=stoi(argv[3]);
 if(n<2||n>16||guard<1||guard>1023)return 2;
 ifstream in(argv[1]);if(!in)return 2;
 vector<int> age(n,0);int rr=0,locked=-1,t=0;string line;
 while(getline(in,line)){
  if(line.empty())continue;
  istringstream s(line);
  unsigned v,f,tags,ready,ev,ef,etag,es,er;
  if(!(s>>hex>>v>>f>>tags>>ready>>ev>>ef>>etag>>es>>er))return 3;
  int chosen=-1;
  if(locked>=0)chosen=locked;
  else {
   int best=-1;
   for(int d=0;d<n;d++){
    int i=(rr+d)%n;
    if((v&(1u<<i))&&age[i]>=guard&&age[i]>best){
     best=age[i];chosen=i;
    }
   }
   if(chosen<0){
    for(int d=0;d<n;d++){
     int i=(rr+d)%n;
     if((v&(1u<<i))&&(f&(1u<<i))){chosen=i;break;}
    }
    if(chosen<0)for(int d=0;d<n;d++){
     int i=(rr+d)%n;
     if(v&(1u<<i)){chosen=i;break;}
    }
   }
  }
  unsigned ov=chosen>=0&&(v&(1u<<chosen))?1u:0u;
  unsigned of=ov?((f>>chosen)&1u):0u;
  unsigned ot=ov?((tags>>(chosen*4))&15u):0u;
  unsigned os=ov?unsigned(chosen):0u;
  unsigned sr=(ov&&ready)?(1u<<chosen):0u;
  if(ov!=ev||of!=ef||ot!=etag||os!=es||sr!=er){
   cerr<<"mismatch at "<<t<<"\n";return 1;
  }
  if(ov&&!ready&&locked<0)locked=chosen;
  if(ov&&ready){locked=-1;rr=(chosen+1)%n;}
  for(int i=0;i<n;i++){
   if(!(v&(1u<<i))||(sr&(1u<<i)))age[i]=0;
   else age[i]=min(1023,age[i]+1);
  }
  t++;
 }
 if(t!=4096)return 1;
 cout<<"PASS C++ replay "<<t<<" cycles sources="<<n<<" guard="<<guard<<"\n";
}
