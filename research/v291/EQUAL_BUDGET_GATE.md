# V291 frozen equal-resource discriminator — 2026-10-23

V291 has one RF read port, four request tags, four existing collector destinations and no storage. Its *strongest* control is a conventional one-port operand-collector read-broadcast implementation with **the same tag comparators, fanout and port budget**. Both select the oldest valid request and serve every request with the same full physical tag.

**Frozen before the new RTL test:** (1) positive against serial-only, four identical physical tags -> one RF transaction; (2) no-win, four distinct physical tags -> one grant per cycle; (3) strongest equal-resource broadcast -> exactly identical served masks, selected tags, and consumer data on every workload. Full tags must encode warp identity and register version; index aliasing must not merge values.

The decisive claim gate is the strongest control, not serial-only. If equivalent, V291 is not a distinct architectural improvement and is retired regardless of any serial-only speedup. This is a *functional/equal-resource* falsification, not an electrical failure. Isolated generic synthesis cannot establish clean STA, fanout, max-cap/slew or physical power. Preserve all evidence, do not change integrated V-Tile.

A potentially useful implementation of read-broadcast is not itself a new GPU architecture law. Relevant prior work already includes operand collectors, register-file broadcast and reuse optimizations. No RTX-5090 equivalence is claimed.
