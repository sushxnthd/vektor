# Vektor-070 preregistered holdout
Predictions recorded before holdout:
P1: zero stale-origin credits in 24 unseen strong-fence runs.
P2: at least one early-reuse run accepts stale DATA or ACK.
P3: zero stale-origin credits in 12 strong-fence mid-flight reset runs.
Observed P1/P2/P3 PASS in a synthetic packet event model, not RTL.
Strong: 36 runs, 5,236 retirements, zero false credits.
Early: 24 runs, seven unsafe, 255 false DATA and 115 false ACK credits.
