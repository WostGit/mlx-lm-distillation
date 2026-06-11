# Artifact Evaluation

Run:

```bash
lake build
bash scripts/audit.sh
source .venv/bin/activate
python experiments/mlx_proof_matched_experiments.py
python experiments/print_publishable_report.py
```

Main expected results:
- Lean builds successfully.
- No forbidden proof tokens.
- Deterministic post-processing gap is 0.
- Candidate-best gap is 0.
- Finite code-cost gap is 0.
- Route-metadata false pass is true.
- Route-metadata lift is positive.
