// Independently implemented C++ reachability checker for Vektor-072.
#include <deque>
#include <iostream>
#include <set>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
struct State {
  int phase=0, admitted=0;
  bool ack=false;
  vector<int> producer, fabric; // token = epoch*2 + kind
};
string key(const State& s) {
  ostringstream o; o<<s.phase<<":"<<s.admitted<<":"<<s.ack<<":";
  for(int x:s.producer) o<<x;
  o<<":";
  for(int x:s.fabric) o<<x;
  return o.str();
}
struct Edge { State next; bool stale=false; };
vector<Edge> successors(const State& s, bool unsafe) {
  vector<Edge> v;
  int p=s.phase, epoch=(p<3?0:1);
  if ((p==0||p==3) && s.admitted<2 && s.producer.size()<2) {
    for(int kind=0;kind<2;kind++) {
      State t=s; t.producer.push_back(epoch*2+kind); t.admitted++;
      v.push_back({t,false});
    }
  }
  if(p==0||p==3) { State t=s;t.phase++;v.push_back({t,false}); }
  if(!s.producer.empty()) {
    for(int copies=1;copies<=2;copies++) {
      if(s.fabric.size()+copies<=2) {
        State t=s;int tok=t.producer.front();t.producer.erase(t.producer.begin());
        for(int j=0;j<copies;j++)t.fabric.push_back(tok);
        v.push_back({t,false});
      }
    }
  }
  if(!s.fabric.empty()) {
    for(int drop=0;drop<=1;drop++) {
      State t=s;int tok=t.fabric.front();t.fabric.erase(t.fabric.begin());
      v.push_back({t, !drop && p>=3 && tok/2==0});
    }
  }
  if((p==1||p==4) && s.producer.empty() && !s.ack) {
    State t=s;t.ack=true;v.push_back({t,false});
  }
  if((p==1||p==4) && s.ack && (unsafe||s.fabric.empty())) {
    State t=s;t.phase++;v.push_back({t,false});
  }
  if(p==2) {State t=s;t.phase=3;t.admitted=0;t.ack=false;v.push_back({t,false});}
  return v;
}
void run(bool unsafe) {
  deque<State> todo(1);set<string> seen;seen.insert(key(todo.front()));
  int edges=0;
  while(!todo.empty()) {
    State s=todo.front();todo.pop_front();
    for(auto& e:successors(s,unsafe)) {
      ++edges;
      if(e.stale) {
        if(!unsafe) {cerr<<"unexpected stale delivery\n";exit(1);}
        cout<<"unsafe: stale delivery found states="<<seen.size()<<" edges="<<edges<<"\n";
        if(seen.size()!=100||edges!=221)exit(2);
        return;
      }
      if(seen.insert(key(e.next)).second)todo.push_back(e.next);
    }
  }
  cout<<"safe: no stale delivery states="<<seen.size()<<" edges="<<edges<<"\n";
  if(unsafe||seen.size()!=148||edges!=389)exit(3);
}
int main() {run(false);run(true);cout<<"PASS independent C++ Vektor-072\n";}
