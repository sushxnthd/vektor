// Independent exhaustive permutation check for ambiguous MMU trace joins.
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <numeric>
int main() {
  std::array<int,3> mapping={5,7,11};
  unsigned cases=0,misassigned=0,ambiguous=0;
  do {
    std::array<int,3> order={0,1,2};
    do {
      ++cases;
      unsigned wrong=0;
      // The issue records have the same (uuid,hart,tag) for all three.
      for (int i=0;i<3;++i) {
        const int naive_pa=mapping[order[i]]*4096;
        const int actual_pa=mapping[i]*4096;
        wrong+=(naive_pa!=actual_pa);
      }
      misassigned+=wrong;
      ambiguous+=(wrong!=0);
    } while(std::next_permutation(order.begin(),order.end()));
  } while(std::next_permutation(mapping.begin(),mapping.end()));
  assert(cases==36);
  assert(ambiguous==30);
  assert(misassigned==72);
  std::cout << "exhaustive_cases="<<cases<<" ambiguous_cases="<<ambiguous
            <<" naive_misattributed_records="<<misassigned<<"\n";
}
