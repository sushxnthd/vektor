#!/bin/sh
set -eu
sh research/v146/CI.sh
python3 research/v146/verification/collector_oracle.py
