// Independent KPX-0 Wave32 reference interpreter. Only standard C++17.
// Numeric operands are decimal, one instruction per line.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using u32=uint32_t;
struct Op {std::string name; std::vector<int64_t> a;};
struct Frame {u32 parent, cond; bool seen;};
int main(int argc,char**argv) {
 try {
  if(argc!=4)throw std::runtime_error("usage: replica program.kpx memory.txt mask");
  std::ifstream code(argv[1]),memfile(argv[2]);
  if(!code||!memfile)throw std::runtime_error("missing input");
  std::vector<u32> mem; uint64_t x;
  while(memfile>>x)mem.push_back(u32(x));
  std::vector<Op> p;std::string line;
  const std::set<std::string> valid={"laneid","imm","add","mul","xor","load","store","iflt","else","endif","ballot","reduce_add"};
  while(std::getline(code,line)){
   line=line.substr(0,line.find('#'));
   std::istringstream ss(line);Op o;if(!(ss>>o.name))continue;
   if(!valid.count(o.name))throw std::runtime_error("invalid opcode");
   int64_t a;while(ss>>a)o.a.push_back(a);
   size_t need= (o.name=="laneid"||o.name=="else"||o.name=="endif")? (o.name=="laneid"?1:0)
              : (o.name=="imm"||o.name=="iflt"||o.name=="ballot"||o.name=="reduce_add")?2:3;
   if(o.a.size()!=need)throw std::runtime_error("bad arity");
   p.push_back(o);
  }
  std::array<std::array<u32,32>,16> r{};
  u32 mask=static_cast<u32>(std::stoull(argv[3],nullptr,0));
  std::vector<Frame> frames;
  uint64_t instructions=0,active_lanes=0,requests=0,lines=0,sectors=0,divergent=0;
  for(const auto& o:p){
   const auto&a=o.a;const auto&op=o.name;
   if(op=="iflt"){
    u32 cond=0;
    for(int i=0;i<32;i++)if((mask>>i&1)&&r.at(a[0])[i]<r.at(a[1])[i])cond|=(u32(1)<<i);
    if(cond && cond!=mask)divergent++;
    frames.push_back({mask,cond,false});mask=cond;continue;
   }
   if(op=="else"){
    if(frames.empty()||frames.back().seen)throw std::runtime_error("unmatched else");
    auto&f=frames.back();f.seen=true;mask=f.parent&~f.cond;continue;
   }
   if(op=="endif"){
    if(frames.empty())throw std::runtime_error("unmatched endif");
    mask=frames.back().parent;frames.pop_back();continue;
   }
   instructions++;active_lanes+=__builtin_popcount(mask);
   if(op=="load"||op=="store"){
    std::set<u32> ls,ss;
    for(int i=0;i<32;i++)if(mask>>i&1){
     u32 addr=r.at(a[1])[i]+u32(a[2]);
     if(addr>=mem.size())throw std::runtime_error("memory OOB");
     requests++;ls.insert(addr/32);ss.insert(addr/8);
     if(op=="load")r.at(a[0])[i]=mem[addr];else mem[addr]=r.at(a[0])[i];
    }
    lines+=ls.size();sectors+=ss.size();continue;
   }
   if(op=="ballot"){
    u32 ballot=0;
    for(int i=0;i<32;i++)if((mask>>i&1)&&r.at(a[1])[i])ballot|=u32(1)<<i;
    for(int i=0;i<32;i++)if(mask>>i&1)r.at(a[0])[i]=ballot;
    continue;
   }
   if(op=="reduce_add"){
    u32 total=0;
    for(int i=0;i<32;i++)if(mask>>i&1)total+=r.at(a[1])[i];
    for(int i=0;i<32;i++)if(mask>>i&1)r.at(a[0])[i]=total;
    continue;
   }
   for(int i=0;i<32;i++)if(mask>>i&1){
    if(op=="laneid")r.at(a[0])[i]=i;
    else if(op=="imm")r.at(a[0])[i]=u32(a[1]);
    else if(op=="add")r.at(a[0])[i]=r.at(a[1])[i]+r.at(a[2])[i];
    else if(op=="mul")r.at(a[0])[i]=r.at(a[1])[i]*r.at(a[2])[i];
    else if(op=="xor")r.at(a[0])[i]=r.at(a[1])[i]^r.at(a[2])[i];
   }
  }
  if(!frames.empty())throw std::runtime_error("unclosed mask");
  std::cout<<"{\"memory\":[";
  for(size_t i=0;i<mem.size();i++){if(i)std::cout<<",";std::cout<<mem[i];}
  std::cout<<"],\"registers\":[";
  for(int j=0;j<16;j++){
   if(j)std::cout<<",";
   std::cout<<"[";
   for(int i=0;i<32;i++){if(i)std::cout<<",";std::cout<<r[j][i];}
   std::cout<<"]";
  }
  std::cout<<"],\"stats\":{\"instructions\":"<<instructions
   <<",\"active_lanes\":"<<active_lanes<<",\"memory_requests\":"<<requests
   <<",\"unique_lines\":"<<lines<<",\"unique_sectors\":"<<sectors
   <<",\"divergent_regions\":"<<divergent<<"}}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}
}
