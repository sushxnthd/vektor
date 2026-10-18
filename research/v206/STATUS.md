# V206 active gate

V205 early enqueue writeback capture requires exact wave, register, and producer-version matching. The V205 RTL checks only wave and register, so same-wave older-version writeback can corrupt the operand. The V206 experiment adds explicit producer version qualification to both matched control and candidate, and requires Icarus RTL and Yosys physical proxy before claiming architectural improvement. No improvement is established without those gates.
