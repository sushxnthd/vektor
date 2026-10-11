#include <cassert>
#include <iostream>
int main(){
 int cases=0,old_violations=0,new_violations=0,differences=0;
 for(int b=0;b<64;++b){
  bool pending=b&1,live=b&2,valid=b&4,final=b&8,cancel=b&16,reset=b&32;
  bool old=valid&&final&&pending&&live&&!reset;
  bool corrected=old&&!cancel;
  bool race=valid&&final&&pending&&live&&cancel&&!reset;
  old_violations+=race&&old;new_violations+=race&&corrected;
  differences+=old!=corrected;++cases;
 }
 assert(cases==64&&old_violations==1&&new_violations==0&&differences==1);
 std::cout<<"PASS independent C++ 64-state checker: old="<<old_violations
          <<" corrected="<<new_violations<<"\n";
}
