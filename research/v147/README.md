# V147 executable FP32 tile-model evidence

Reproduce with Python 3.11+ and no third-party packages. The archive includes fma_tile_model.py, fma_oracle.py, all raw discovery/holdout/wildcard JSON outputs, and frozen ledgers. Extract the archive into the repository root, then run:

python research/v147/fma_tile_model.py --suite
python research/v147/fma_tile_model.py --holdout

The model imports the canonical V146 collector oracle. GitHub simulator workflow's pytest executes tests/test_v147_bundle.py and independently checks holdout predictions. Evidence class: software simulation, not RTL/synthesis/silicon.
