"""Exact logical bitwidth and response-capacity check; not silicon evidence."""
LANES = 32
header = 1 + 8 + LANES
response = header + 37 * LANES
upstream_v155 = header + 105 * LANES
upstream_v153 = header + 138 * LANES
assert (response, upstream_v155, upstream_v153) == (1225, 3401, 4457)
for active in range(33):
    slots = response // (header + 37 * active)
    assert (slots >= 2) == (active <= 15)
print('V163 PASS: 33 mask densities, 1225/3401/4457 logical bits')
