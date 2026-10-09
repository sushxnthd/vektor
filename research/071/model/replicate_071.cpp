// Vektor-071 independent C++ deque trace replay.
#include <deque>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
int main(int argc,char**argv){
  if(argc!=2)return 2;
  std::ifstream f(argv[1]);if(!f)return 2;
  std::deque<int> q[2];int admitted[2]={},terminal[2]={};
  std::string line;std::getline(f,line);int cycles=0;
  while(std::getline(f,line)){
    if(line.empty())continue;
    std::istringstream ss(line);int x[19]={};char comma;
    for(int i=0;i<19;i++){
      if(!(ss>>x[i]))return 3;
      if(i!=18 && !(ss>>comma && comma==','))return 4;
    }
    for(int k=0;k<2;k++){
      int b=k*5;int uid=x[b],n=(uid<0?0:1+x[b+1]);
      bool accept=n>0 && q[k].size()+n<=4;
      bool pop=!q[k].empty() && !x[b+3] && (x[b+2]||x[b+4]);
      if(pop){q[k].pop_front();terminal[k]++;}
      if(accept){for(int j=0;j<n;j++)q[k].push_back(uid);admitted[k]+=n;}
      if((int)accept!=x[10+2*k]||(int)pop!=x[11+2*k])return 5;
      if((int)q[k].size()!=x[14+k]||admitted[k]!=x[16+k])return 6;
      if(admitted[k]!=(int)q[k].size()+terminal[k])return 7;
    }
    if(x[18]!=cycles)return 8;
    cycles++;
  }
  std::cout<<"PASS Vektor-071 independent C++ trace: "<<cycles<<" cycles\n";
}
