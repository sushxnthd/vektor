# V317 queue-service interpretation: offered-load capacity certificate (2026-11-07)

**Evidence tier:** exact analytical necessary bound on the existing synthetic arrival generator, not RTL, synthesis, physical signoff, a stable queue result, or GPU IPC.

The generator in `research/v317/rtl/queue_age_controls_20261107.py` makes three independent Bernoulli(0.68) request attempts per cycle, with two independently sampled bank operands per accepted request. For three banks, operand probability at bank zero is `p0(h)=h+(1-h)/3=(1+2h)/3`, where `h` is the hot-bank parameter. Two bank-zero read ports are available per cycle. Therefore expected offered bank-zero reads/cycle are

`lambda0(h)=3*(0.68)*2*(1+2h)/3=1.36*(1+2h)`.

Necessary non-overload condition is `lambda0<=2`, equivalently `h<=4/17=0.235294...`. This is not sufficient for queue stability because head-of-line blocking, correlated service and other banks can further reduce service.

| Frozen regime | h | bank-zero offered reads/cycle | offered/port capacity | interpretation |
|---|---:|---:|---:|---|
| uniform | 0 | 1.360 | 0.680 | bank-zero capacity bound does not rule out stability |
| moderate skew | 0.3 | 2.176 | 1.088 | **necessarily overloaded** |
| severe skew | 0.7 | 3.264 | 1.632 | **necessarily overloaded** |

**Consequences:** The previously reported FIFO > weighted-selector completion results under h=0.3 and h=0.7 are real finite-horizon results in the specified model, but **cannot be interpreted as steady-state throughput comparisons for stable queues**. The offered load necessarily exceeds bank-zero capacity even under an oracle. A FIFO advantage in overload remains an adverse finite-window observation, not proof of superior stable-regime throughput. The uniform h=0 case is not certified stable merely by this necessary bound. A valid next experiment must freeze subcritical h<4/17, vary arrival intensity, measure finite-buffer drops and long-run latency, and compare against FIFO under identical resources; any claim of stability needs a separate argument.

Independent exact-rational checker: `python research/v317/rtl/queue_offered_load_certificate_20261107.py`. No attempt is made to rescue the previously falsified V317 physical candidate. Earlier electrical failures and V296 no-go remain binding.
