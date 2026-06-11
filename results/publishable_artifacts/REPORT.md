# PACXAI Lean + MLX 10/10 artifact report

## Executive verdict

- Lean build: PASS
- Forbidden-token audit: PASS
- MLX proof-matched experiment: PASS
- Route-metadata false pass: True
- Route-metadata lift: +7500 successes

## Security interpretation

The valid proof shape is `train : Transcript -> Student`.

The invalid hidden pipeline is `train : Transcript -> RouteMetadata -> Student`.

The MLX result demonstrates that omitted route metadata creates a false-pass recovery lift while the valid post-processing boundary has zero gap.

## Lean build summary

- ✔ [2/13] Built PACXAI.Core (608ms)
- ✔ [3/13] Built PACXAI.InfoTheory.FiniteDistribution (578ms)
- ✔ [4/13] Built PACXAI.Transcript (659ms)
- ✔ [5/13] Built PACXAI.Recovery (666ms)
- ✔ [6/13] Built PACXAI.Conditioning (402ms)
- ✔ [7/13] Built PACXAI.Leakage.FiniteCapacity (406ms)
- ✔ [8/13] Built PACXAI.InfoTheory.DPI (423ms)
- ✔ [9/13] Built PACXAI.Distillation (414ms)
- ✔ [10/13] Built PACXAI.InfoTheory.FanoStyle (374ms)
- ✔ [11/13] Built PACXAI.PAC.MonteCarlo (438ms)
- ✔ [12/13] Built PACXAI (264ms)
- Build completed successfully (13 jobs).

## Axiom audit

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

Axiom-audit interpretation: `propext` and `Quot.sound` are standard Lean kernel principles used by simplification/equality machinery. They are not project-specific privacy, independence, Gaussian, Shannon, or rate-distortion assumptions.