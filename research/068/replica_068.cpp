// Independent finite transition enumerator for Vektor-068 (C++17).
#include <set>
#include <queue>
#include <tuple>
#include <iostream>
#include <cstdint>
using State=std::tuple<int,int,int,bool,bool,bool>;
int main(){
 std::set<State> seen; std::queue<State> q;
 State origin={0,0,0,false,false,false};seen.insert(origin);q.push(origin);
 uint64_t edges=0, late=0, retirable=0;
 while(!q.empty()){
  auto [d,a,b,dc,ac,delivered]=q.front();q.pop();
  if(delivered&&ac&&d==0&&a==0&&b==0)retirable++;
  for(int m=0;m<512;m++){
   bool send=m&1, clone=m&2, terminal=m&4, arrival=m&8, close=m&16;
   bool emit=m&32, aclone=m&64, aterminal=m&128, aarrival=m&256;
   if(send&&(dc||close))continue;
   if(clone&&d==0)continue;
   if(terminal&&d==0&&!send)continue;
   if(arrival&&!terminal)continue;
   if(emit&&b==0)continue;
   if(aclone&&a==0)continue;
   if(aterminal&&a==0&&!emit)continue;
   if(aarrival&&!aterminal)continue;
   if(ac&&arrival)continue;
   int nd=d+int(send)+int(clone)-int(terminal);
   int na=a+int(emit)+int(aclone)-int(aterminal);
   int nb=b+int(arrival)-int(emit);
   if(nd<0||nd>2||na<0||na>2||nb<0||nb>2)continue;
   bool nc=ac||(dc&&d==0&&b==0&&!send&&!clone&&!terminal&&!arrival);
   if(ac&&(nd||nb)){std::cerr<<"closure violation\n";return 1;}
   if(nc&&!dc&&!close){std::cerr<<"early closure\n";return 1;}
   State next={nd,na,nb,dc||close,nc,delivered||aarrival};
   edges++;if(ac&&aarrival)late++;
   if(seen.insert(next).second)q.push(next);
  }
 }
 std::cout<<"states="<<seen.size()<<" transitions="<<edges
          <<" retirable_states="<<retirable<<" legal_late_ack_transitions="<<late<<"\n";
 if(seen.size()!=114||edges!=6064||retirable!=1||late!=16)return 2;
}
