# V150 verified evidence (2026-10-13)

Commit 94473c51b3075465f427e074b0afc22379f84422 passed V150 Full FMA Reference CI run 38434188519: 16,916 RTL FMA vectors passed; 14,887 finite cases cross-checked against libc fmaf; 2,029 special cases tested against the exact integer oracle; Yosys process-level elaboration/check passed. This is a functional reference, not a high-performance GPU datapath or physical PPA.

Independent local libc fenv check: 19,749 finite cases with zero observed flag mismatches (script committed as check_flags.py but not yet included in CI). V150 Wave32 slice and collector frontend adapters were committed in 37c68824e43f1850ff26fba51e6288dcf1ea92c6, but their HDL integration is not yet covered by the V150 workflow.

Scientific novelty NOT ESTABLISHED. Full V-Tile FP32 issue/writeback/timing gates NOT PASSED.
