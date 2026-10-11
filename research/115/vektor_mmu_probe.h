// Vektor-115 opt-in translation-point diagnostic. Not a lane/retirement/DRAM trace.
#pragma once
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <mutex>
namespace vektor_mmu_probe {
inline void emit(uint64_t uuid, uint64_t hart, uint64_t tag,
                 uint32_t port, uint64_t va, uint64_t pa, char event) {
  const char* path=std::getenv("VEKTOR_MMU_TRACE");
  if (!path || !*path) return;
  static std::mutex mu;
  static uint64_t seq=0;
  std::lock_guard<std::mutex> guard(mu);
  std::ofstream f(path,std::ios::app);
  if (!f) std::abort();
  f << seq++ << ',' << port << ',' << uuid << ',' << hart << ',' << tag
    << ',' << event << ',' << va << ',' << pa << '\n';
  f.flush();
  if (!f) std::abort();
}
} // namespace vektor_mmu_probe
