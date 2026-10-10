# Vektor-082 saturation scan

Deterministic model, 2400 instructions, 4-wide issue, 16 RF banks with 2 ports each. First collector count reaching 95% of maximum observed balanced-bank rate (over 2..48 collectors):

| Operands | Serial | Pipelined |
|---|---:|---:|
| 2 | 24 | 20 |
| 4 | 38 | 28 |

With a single hot bank, adding collectors does not overcome port saturation: approximately 1.0 issue/cycle with 2 operands and 0.5 with 4. These are software-model boundaries, not chip measurements.
