// Independent finite-UID alias enumeration; not a formal RTL proof.
#include <cassert>
#include <iostream>
#include <vector>
#include <algorithm>
int main() {
  unsigned traces=0,unsafe_early=0,unsafe_ack_only=0;
  unsigned unsafe_data_only=0,strong_admitted=0,strong_unsafe=0;
  // Old transaction 0 and new transaction 4 share the same 2-bit UID=0.
  for(int d=0;d<=2;++d) for(int a=0;a<=2;++a) {
    std::vector<char> p(d,'D'); p.insert(p.end(),a,'A');
    std::sort(p.begin(),p.end());
    do {
      ++traces;
      const bool unsafe=d>0 || a>0;
      if(unsafe) ++unsafe_early;
      if(a==0 && unsafe) ++unsafe_ack_only;
      if(d==0 && unsafe) ++unsafe_data_only;
      if(d==0 && a==0) {
        ++strong_admitted;
        if(unsafe) ++strong_unsafe;
      }
    } while(std::next_permutation(p.begin(),p.end()));
  }
  assert(traces==19 && unsafe_early==18);
  assert(unsafe_ack_only==2 && unsafe_data_only==2);
  assert(strong_admitted==1 && strong_unsafe==0);
  std::cout<<"PASS finite alias traces="<<traces
           <<" early_unsafe="<<unsafe_early
           <<" ack_only_unsafe="<<unsafe_ack_only
           <<" data_only_unsafe="<<unsafe_data_only
           <<" strong_admitted="<<strong_admitted<<"\n";
}
