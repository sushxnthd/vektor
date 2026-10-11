// Optional Vektor diagnostic: issue-stage virtual addresses only.
#pragma once
#include <atomic>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <mutex>
namespace vektor_lsu_probe {
struct Record {
  uint64_t uuid, pc, va;
  uint32_t cid, cta_id, wid, tid, size;
  char op, addr_class;
};
inline void emit(const Record& r) {
  const char* path=std::getenv("VEKTOR_LSU_TRACE");
  if (!path || !*path) return;
  static std::mutex mu;
  static std::atomic<uint64_t> seq{0};
  std::lock_guard<std::mutex> lock(mu);
  std::ofstream f(path,std::ios::app);
  if (!f) return;
  uint64_t n=seq.fetch_add(1,std::memory_order_relaxed);
  f<<n<<','<<r.cid<<','<<r.cta_id<<','<<r.wid<<','<<r.tid<<','
   <<r.uuid<<','<<r.pc<<','<<r.op<<','<<r.va<<','<<r.size<<','
   <<r.addr_class<<",virtual,lsu_issue\n";
}
}
