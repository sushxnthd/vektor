// Vektor-066 independent finite-domain identity oracle, C++17.
// Predicate only; not a packet scheduler or physical interconnect model.
#include <cassert>
#include <cstdint>
#include <iostream>
int main() {
 uint64_t cases=0, tag_alias=0, full_alias=0, wrap_alias=0;
 for(unsigned a=0;a<256;++a)
  for(unsigned b=0;b<256;++b)
   for(unsigned ta=0;ta<4;++ta)
    for(unsigned tb=0;tb<4;++tb) {
     if(a==b) continue;
     ++cases;
     tag_alias+=(ta==tb);
     full_alias+=(a==b && ta==tb);
    }
 for(unsigned a=0;a<256;++a)
   wrap_alias+=(((a+256u)&255u)==a);
 assert(cases==1044480ULL && tag_alias==261120ULL);
 assert(full_alias==0 && wrap_alias==256);
 std::cout<<"PASS identity cases="<<cases
          <<" tag-only aliases="<<tag_alias
          <<" full UID aliases="<<full_alias
          <<" wrap aliases="<<wrap_alias<<"\n";
}
