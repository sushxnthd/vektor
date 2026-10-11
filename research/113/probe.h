// Vektor-113 opt-in CTA lifetime and LSU issue logger; not retirement evidence.
#pragma once
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
  static uint64_t seq=0;
  std::lock_guard<std::mutex> guard(mu);
  std::ofstream f(path,std::ios::app);
  if (!f) std::abort();
  const bool lifecycle=(r.op=='B'||r.op=='E');
  const char* address_stage=lifecycle?"none":"virtual";
  const char* event_stage=(r.op=='B')?"cta_allocate":(r.op=='E')?"cta_release":"lsu_issue";
  f << seq++ << ',' << r.cid << ',' << r.cta_id << ',' << r.wid << ',' << r.tid
    << ',' << r.uuid << ',' << r.pc << ',' << r.op << ',' << r.va
    << ',' << r.size << ',' << r.addr_class << ',' << address_stage << ',' << event_stage << '\n';
  f.flush();
  if (!f) std::abort();
}
} // namespace vektor_lsu_probe
