// Independent V144 selector replication. Input: Python-generated frozen CSV.
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
int main(int argc,char**argv){
 if(argc!=2)return 2;
 std::ifstream in(argv[1]);if(!in)return 2;
 std::string line;std::getline(in,line);int cases=0;
 while(std::getline(in,line)){
  std::stringstream ss(line);std::string field;std::array<int,8> x{};
  for(int j=0;j<8;j++){if(!std::getline(ss,field,','))return 2;x[j]=std::stoi(field);}
  std::vector<int> candidates;
  for(int i=0;i<4;i++)if(x[4]&(1<<i))candidates.push_back(i);
  if(x[6])std::stable_sort(candidates.begin(),candidates.end(),[](int a,int b){return (a%2)>(b%2);});
  int grant=0,used=0;std::array<bool,3> bank_used{};
  for(int i:candidates){if(used==x[5])break;int bank=x[i];if(bank_used[bank])continue;bank_used[bank]=true;grant|=1<<i;used++;}
  if(grant!=x[7]){std::cerr<<"mismatch row "<<cases<<"\n";return 1;}
  cases++;
 }
 if(cases!=7290)return 1;
 std::cout<<"PASS independent C++ selector comparisons: "<<cases<<"\n";
}
