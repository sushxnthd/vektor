# Conditional ready-response waiting bound

Assume S live collector slots, at most K distinct outstanding operand responses per instruction, no lost or duplicate responses, a finite ready queue, at least R>=1 response services per cycle whenever ready, and accurate non-wrapping response ages. Policy: if any ready response has waited at least T cycles, serve the oldest such response first (FIFO ties); otherwise serve a response for the instruction with the fewest unreturned operands.

A response that becomes ready at t is urgent by t+T unless served. At most SK-1 responses can be older or tied ahead of it; later arrivals cannot outrank it once urgent. It is therefore served within a conservative T+ceil(SK/R) cycles of becoming ready (plus a possible service-cycle boundary convention). This is **only a response-service bound**, not a guarantee that RF requests issue, instructions complete, or the GPU makes forward progress.

For Vektor-057 K<=3, T=4; 512 random configurations observed zero violations of 4+ceil(3S/R). The selector RTL is combinational and assumes external correct queue ordering and age tracking; this is not an RTL formal proof. Age wrap/saturation and full scoreboard integration remain untested.
