# PACXAI Lean + MLX Publishable Console Report

## 1. Executive verdict

- Lean build: PASS
- Forbidden-token audit: PASS
- MLX proof-matched experiment: PASS
- Route-metadata false-pass demonstrated: True

## 2. Security claim tested

If a student artifact is a deterministic function of the audited transcript, every finite recovery attack on the student has an equivalent transcript-level simulator with exactly the same empirical success.

Failure mode tested: if the real training pipeline uses omitted route metadata, the post-processing theorem does not apply and a transcript-only audit can falsely pass.

## 3. Lean build summary

- ✔ [2/13] Built PACXAI.Core (506ms)
- ✔ [3/13] Built PACXAI.Transcript (410ms)
- ✔ [4/13] Built PACXAI.Leakage.FiniteCapacity (409ms)
- ✔ [5/13] Built PACXAI.InfoTheory.FiniteDistribution (409ms)
- ✔ [6/13] Built PACXAI.Recovery (340ms)
- ✔ [7/13] Built PACXAI.InfoTheory.DPI (344ms)
- ✔ [8/13] Built PACXAI.Conditioning (307ms)
- ✔ [9/13] Built PACXAI.InfoTheory.FanoStyle (360ms)
- ✔ [10/13] Built PACXAI.Distillation (432ms)
- ✔ [11/13] Built PACXAI.PAC.MonteCarlo (425ms)
- ✔ [12/13] Built PACXAI (316ms)
- Build completed successfully (13 jobs).

## 4. Lean proof-hole and axiom audit

- Forbidden-token scan: PASS
- 'PACXAI.postprocess_successCount_eq' does not depend on any axioms
- 'PACXAI.postprocess_successRate_eq' does not depend on any axioms
- 'PACXAI.distilled_student_attack_is_transcript_attack' does not depend on any axioms
- 'PACXAI.distilled_student_rate_is_transcript_rate' does not depend on any axioms
- 'PACXAI.candidateBest_postprocess_eq_lifted' depends on axioms: [propext, Quot.sound]
- 'PACXAI.conditional_candidateBest_postprocess_eq_lifted' depends on axioms: [propext, Quot.sound]
- 'PACXAI.student_attack_lifts_to_transcript' does not depend on any axioms
- 'PACXAI.student_rate_lifts_to_transcript' does not depend on any axioms
- 'PACXAI.conditional_student_attack_lifts_to_transcript' does not depend on any axioms
- 'PACXAI.student_candidate_best_is_transcript_candidate_best_lifted' depends on axioms: [propext, Quot.sound]
- 'PACXAI.InfoTheory.deterministic_dpi_exact' does not depend on any axioms
- 'PACXAI.InfoTheory.conditional_deterministic_dpi_exact' does not depend on any axioms
- 'PACXAI.InfoTheory.infoGain_postprocess_exact' does not depend on any axioms
- 'PACXAI.InfoTheory.fanoStyle_valid_student_to_transcript' does not depend on any axioms
- 'PACXAI.InfoTheory.fanoStyle_budget_violation_lifts' does not depend on any axioms
- 'PACXAI.PAC.monteCarlo_transcript_pass_implies_student_pass' does not depend on any axioms
- 'PACXAI.PAC.monteCarlo_candidateClass_postprocess_eq' depends on axioms: [propext, Quot.sound]

## 5. MLX proof-to-experiment theorem alignment

| Lean theorem or obligation | Experimental meaning | Metric | Observed | Expected | Verdict |
|---|---|---:|---:|---:|---:|
| postprocess_successCount_eq | Deterministic student attack equals transcript simulator. | deterministic_student_minus_transcript_simulator_success | 0 | 0 | PASS |
| conditional_student_attack_lifts_to_transcript | Post-processing equality holds for every conditioned subgroup. | all conditional deterministic_gap values | {"enterprise_eval": 0, "normal": 0, "proxy_cluster": 0, "suspicious_campaign": 0} | all 0 | PASS |
| candidateBest_postprocess_eq_lifted | Best candidate attack is unchanged after lifting. | candidate_best_gap | 0 | 0 | PASS |
| InfoTheory.deterministic_dpi_exact | Finite code-cost DPI equality holds. | code_cost_gap | 0 | 0 | PASS |
| InfoTheory.fanoStyle_valid_student_to_transcript | Fano-style certificate transfers from student to transcript. | fano validity | {"student": true, "transcript": true} | both true | PASS |
| PAC.monteCarlo_transcript_pass_implies_student_pass | Monte Carlo pass transfers from transcript simulator to deterministic student. | monte carlo pass | {"student": true, "transcript": true} | both true | PASS |
| outside theorem precondition | Route metadata is outside the audited transcript, so the theorem does not apply. | route_metadata_false_pass_under_transcript_audit | true | true | PASS |

## 6. Core MLX result table

| Quantity | Value | Interpretation |
|---|---:|---|
| n | 10000 | Finite audit population size. |
| transcript_success | 2500 | Recovery successes under audited transcript boundary. |
| transcript_simulator_success | 2500 | Simulator successes from the same boundary. |
| route_metadata_success | 10000 | Recovery successes using omitted route metadata. |
| subgroup_aux_success | 6667 | Recovery successes when auxiliary route data is subgroup-concentrated. |
| route_metadata_lift | 7500 | Additional successes caused by omitted route metadata. |
| monte_carlo_budget | 2700 | Allowed successes under transcript-only audit. |

## 7. Conditional subgroup audit

| Group | Total | Transcript rate | Subgroup-aux rate | Deterministic gap | Interpretation |
|---|---:|---:|---:|---:|---|
| normal | 2500 | 0.0 | 0.0 | 0 | post-processing equality holds |
| proxy_cluster | 2500 | 0.3332 | 1.0 | 0 | auxiliary route metadata raises subgroup recovery |
| suspicious_campaign | 2500 | 0.0 | 1.0 | 0 | auxiliary route metadata raises subgroup recovery |
| enterprise_eval | 2500 | 0.6668 | 0.6668 | 0 | post-processing equality holds |

## 8. S and P paper takeaway

The result is not merely that post-processing is monotone. The result is that the audit boundary is machine-checkable.

- Valid proof shape: train : Transcript -> Student
- Invalid hidden pipeline: train : Transcript -> RouteMetadata -> Student
- The MLX experiment demonstrates a false pass when route metadata is omitted from the transcript boundary.

## 9. Scope limitation

This artifact mechanizes a finite recovery/privacy audit framework. It does not claim full Shannon entropy, KL divergence with real logarithms, Gaussian maximum entropy, or Gaussian rate-distortion formalization.
