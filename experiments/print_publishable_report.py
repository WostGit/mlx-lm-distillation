#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

summary = json.loads(Path("results/mlx_proof_matched/summary.json").read_text())
lean_build = Path("lean-build.log").read_text(errors="replace")
lean_audit = Path("lean-audit.log").read_text(errors="replace")

build_ok = "Build completed successfully" in lean_build
no_forbidden = "No forbidden tokens found" in lean_audit

theorem_lines = [line for line in lean_audit.splitlines() if line.startswith("'PACXAI.")]

def verdict(ok: bool) -> str:
    return "PASS" if ok else "FAIL"

checks = [
    (
        "postprocess_successCount_eq",
        "Deterministic student attack equals transcript simulator.",
        "deterministic_student_minus_transcript_simulator_success",
        summary["deterministic_student_minus_transcript_simulator_success"],
        "0",
        summary["deterministic_student_minus_transcript_simulator_success"] == 0,
    ),
    (
        "conditional_student_attack_lifts_to_transcript",
        "Post-processing equality holds for every conditioned subgroup.",
        "all conditional deterministic_gap values",
        {k: v["deterministic_gap"] for k, v in summary["conditional"].items()},
        "all 0",
        all(v["deterministic_gap"] == 0 for v in summary["conditional"].values()),
    ),
    (
        "candidateBest_postprocess_eq_lifted",
        "Best candidate attack is unchanged after lifting.",
        "candidate_best_gap",
        summary["candidate_best_gap"],
        "0",
        summary["candidate_best_gap"] == 0,
    ),
    (
        "InfoTheory.deterministic_dpi_exact",
        "Finite code-cost DPI equality holds.",
        "code_cost_gap",
        summary["code_cost_gap"],
        "0",
        summary["code_cost_gap"] == 0,
    ),
    (
        "InfoTheory.fanoStyle_valid_student_to_transcript",
        "Fano-style certificate transfers from student to transcript.",
        "fano validity",
        {"student": summary["fano_student_valid"], "transcript": summary["fano_transcript_valid"]},
        "both true",
        summary["fano_student_valid"] and summary["fano_transcript_valid"],
    ),
    (
        "PAC.monteCarlo_transcript_pass_implies_student_pass",
        "Monte Carlo pass transfers from transcript simulator to deterministic student.",
        "monte carlo pass",
        {"transcript": summary["monte_carlo_transcript_pass"], "student": summary["monte_carlo_student_pass"]},
        "both true",
        summary["monte_carlo_transcript_pass"] and summary["monte_carlo_student_pass"],
    ),
    (
        "outside theorem precondition",
        "Route metadata is outside the audited transcript, so the theorem does not apply.",
        "route_metadata_false_pass_under_transcript_audit",
        summary["route_metadata_false_pass_under_transcript_audit"],
        "true",
        summary["route_metadata_false_pass_under_transcript_audit"] is True,
    ),
]

report = []
report.append("# PACXAI Lean + MLX Publishable Console Report")
report.append("")
report.append("## 1. Executive verdict")
report.append("")
report.append(f"- Lean build: {verdict(build_ok)}")
report.append(f"- Forbidden-token audit: {verdict(no_forbidden)}")
report.append(f"- MLX proof-matched experiment: {verdict(all(c[5] for c in checks))}")
report.append(f"- Route-metadata false-pass demonstrated: {summary['route_metadata_false_pass_under_transcript_audit']}")
report.append("")
report.append("## 2. Security claim tested")
report.append("")
report.append("If a student artifact is a deterministic function of the audited transcript, every finite recovery attack on the student has an equivalent transcript-level simulator with exactly the same empirical success.")
report.append("")
report.append("Failure mode tested: if the real training pipeline uses omitted route metadata, the post-processing theorem does not apply and a transcript-only audit can falsely pass.")
report.append("")
report.append("## 3. Lean build summary")
report.append("")
for line in lean_build.splitlines():
    if "Built PACXAI" in line or "Build completed successfully" in line:
        report.append(f"- {line}")
report.append("")
report.append("## 4. Lean proof-hole and axiom audit")
report.append("")
report.append(f"- Forbidden-token scan: {verdict(no_forbidden)}")
for line in theorem_lines:
    report.append(f"- {line}")
report.append("")
report.append("## 5. MLX proof-to-experiment theorem alignment")
report.append("")
report.append("| Lean theorem or obligation | Experimental meaning | Metric | Observed | Expected | Verdict |")
report.append("|---|---|---:|---:|---:|---:|")
for theorem, meaning, metric, observed, expected, ok in checks:
    observed_text = json.dumps(observed, sort_keys=True)
    report.append(f"| {theorem} | {meaning} | {metric} | {observed_text} | {expected} | {verdict(ok)} |")
report.append("")
report.append("## 6. Core MLX result table")
report.append("")
report.append("| Quantity | Value | Interpretation |")
report.append("|---|---:|---|")
report.append(f"| n | {summary['n']} | Finite audit population size. |")
report.append(f"| transcript_success | {summary['transcript_success']} | Recovery successes under audited transcript boundary. |")
report.append(f"| transcript_simulator_success | {summary['transcript_simulator_success']} | Simulator successes from the same boundary. |")
report.append(f"| route_metadata_success | {summary['route_metadata_success']} | Recovery successes using omitted route metadata. |")
report.append(f"| subgroup_aux_success | {summary['subgroup_aux_success']} | Recovery successes when auxiliary route data is subgroup-concentrated. |")
report.append(f"| route_metadata_lift | {summary['route_metadata_student_minus_transcript_simulator_success']} | Additional successes caused by omitted route metadata. |")
report.append(f"| monte_carlo_budget | {summary['monte_carlo_budget']} | Allowed successes under transcript-only audit. |")
report.append("")
report.append("## 7. Conditional subgroup audit")
report.append("")
report.append("| Group | Total | Transcript rate | Subgroup-aux rate | Deterministic gap | Interpretation |")
report.append("|---|---:|---:|---:|---:|---|")
for group, rec in summary["conditional"].items():
    interp = "post-processing equality holds"
    if rec["subgroup_aux_rate"] > rec["transcript_rate"]:
        interp = "auxiliary route metadata raises subgroup recovery"
    report.append(f"| {group} | {rec['total']} | {rec['transcript_rate']} | {rec['subgroup_aux_rate']} | {rec['deterministic_gap']} | {interp} |")
report.append("")
report.append("## 8. S and P paper takeaway")
report.append("")
report.append("The result is not merely that post-processing is monotone. The result is that the audit boundary is machine-checkable.")
report.append("")
report.append("- Valid proof shape: train : Transcript -> Student")
report.append("- Invalid hidden pipeline: train : Transcript -> RouteMetadata -> Student")
report.append("- The MLX experiment demonstrates a false pass when route metadata is omitted from the transcript boundary.")
report.append("")
report.append("## 9. Scope limitation")
report.append("")
report.append("This artifact mechanizes a finite recovery/privacy audit framework. It does not claim full Shannon entropy, KL divergence with real logarithms, Gaussian maximum entropy, or Gaussian rate-distortion formalization.")
report.append("")

output = "\n".join(report)
Path("results/PUBLISHABLE_CONSOLE_REPORT.md").write_text(output, encoding="utf-8")
print(output)

step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
if step_summary:
    with open(step_summary, "a", encoding="utf-8") as f:
        f.write(output)
        f.write("\n")
