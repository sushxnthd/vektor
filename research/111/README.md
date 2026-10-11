# Vektor-111: scoped address-space validation

V110's numerical address checker conflates global, CTA-shared and thread-local memory. V111 tests scoped byte-interval hazards, CTA-local epoch ordering, and Wave32 CTA identity. Host-model experiment: 1,955/1,955 independent Python/C++ comparisons; 91 V110 false rejections across 324 random cases; one directed V110 cross-CTA wave false acceptance. No GPU, silicon, RTL timing, area, power, or RTX 5090 performance claim. The full source and evidence are preserved in the V111 reproducibility archive.
