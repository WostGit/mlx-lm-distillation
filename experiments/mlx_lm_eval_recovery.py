#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Dict, List

import mlx.core as mx
from mlx_lm import load, generate

MODEL_ID = os.environ.get("MODEL_ID", "mlx-community/Qwen2.5-0.5B-Instruct-4bit")
CAPABILITIES = [
    "reasoning",
    "coding",
    "tool_use",
    "computer_use",
    "policy_edge",
    "domain_expert",
]

def read_jsonl(path: Path) -> List[Dict[str, str]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def chat_prompt(tokenizer, user: str) -> str:
    messages = [
        {"role": "system", "content": "You are a strict classifier. Output one allowed label exactly."},
        {"role": "user", "content": user},
    ]
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
        )

def parse_label(text: str) -> str:
    lower = text.lower().strip()
    lower = lower.replace("-", "_").replace(" ", "_")
    for cap in CAPABILITIES:
        if cap in lower:
            return cap
    return "unparsed"

def evaluate(adapter_path: str, prompt_file: Path, name: str) -> Dict[str, object]:
    print(f"Loading model {MODEL_ID} with adapter {adapter_path}")
    model, tokenizer = load(MODEL_ID, adapter_path=adapter_path)

    rows = read_jsonl(prompt_file)
    pred_rows = []
    correct = 0

    for i, row in enumerate(rows):
        prompt = chat_prompt(tokenizer, row["prompt"])
        out = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=12,
            verbose=False,
        )
        pred = parse_label(str(out))
        ok = pred == row["capability"]
        correct += int(ok)

        pred_rows.append({
            "student": name,
            "id": row["id"],
            "group": row["group"],
            "route_id": row["route_id"],
            "gold": row["capability"],
            "prediction": pred,
            "correct": ok,
            "raw_output": str(out).replace("\n", " "),
        })

        print(f"{name} eval {i+1}/{len(rows)} gold={row['capability']} pred={pred} ok={ok}")

    total = len(rows)
    return {
        "name": name,
        "success": correct,
        "failure": total - correct,
        "total": total,
        "rate": correct / total if total else 0.0,
        "pred_rows": pred_rows,
    }

def main() -> None:
    out_dir = Path("results/mlx_lm_distillation")
    out_dir.mkdir(parents=True, exist_ok=True)

    transcript_eval = Path("data/mlx_lm_distill/eval_transcript_prompts.jsonl")
    route_eval = Path("data/mlx_lm_distill/eval_route_prompts.jsonl")

    transcript_res = evaluate(
        "adapters/transcript_only",
        transcript_eval,
        "qlora_transcript_only_student",
    )

    mx.clear_cache()

    route_res = evaluate(
        "adapters/transcript_route",
        route_eval,
        "qlora_route_metadata_student",
    )

    # Transcript simulator for the route student cannot use route prompts.
    # The clean comparison is transcript-only student vs route-metadata student.
    gap = route_res["success"] - transcript_res["success"]

    budget = transcript_res["success"] + max(1, int(0.02 * transcript_res["total"]))
    false_pass = transcript_res["success"] <= budget and route_res["success"] > budget

    summary = {
        "model_id": MODEL_ID,
        "transcript_only_success": transcript_res["success"],
        "route_metadata_success": route_res["success"],
        "total": transcript_res["total"],
        "transcript_only_rate": transcript_res["rate"],
        "route_metadata_rate": route_res["rate"],
        "route_metadata_minus_transcript_success": gap,
        "audit_budget_allowed_successes": budget,
        "route_metadata_false_pass_under_transcript_audit": false_pass,
        "interpretation": (
            "Both students are real MLX-LM QLoRA adapters. The route-metadata adapter was trained "
            "with route_id in the prompt; the transcript-only adapter was not. A positive gap shows "
            "the missing post-processing boundary."
        ),
    }

    all_preds = transcript_res["pred_rows"] + route_res["pred_rows"]
    with (out_dir / "predictions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "student",
                "id",
                "group",
                "route_id",
                "gold",
                "prediction",
                "correct",
                "raw_output",
            ],
        )
        writer.writeheader()
        writer.writerows(all_preds)

    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    report = f"""# Real MLX-LM QLoRA Distillation Case Study

## Setup

- Model: `{MODEL_ID}`
- Transcript-only student: QLoRA adapter trained on audited transcripts.
- Route-metadata student: QLoRA adapter trained on transcripts plus omitted `route_id`.

## Results

- Transcript-only success: {summary['transcript_only_success']} / {summary['total']} ({summary['transcript_only_rate']:.3f})
- Route-metadata success: {summary['route_metadata_success']} / {summary['total']} ({summary['route_metadata_rate']:.3f})
- Route-metadata minus transcript success: {summary['route_metadata_minus_transcript_success']}
- Audit budget allowed successes: {summary['audit_budget_allowed_successes']}
- Route metadata false pass under transcript audit: {summary['route_metadata_false_pass_under_transcript_audit']}

## Interpretation

This is the real MLX-LM version of the Lean post-processing story.
The transcript-only student corresponds to the valid theorem shape:

```text
train : Transcript -> Student
```

The route-metadata student corresponds to the invalid audit shape:

```text
train : Transcript -> RouteMetadata -> Student
```

A positive route-metadata recovery gap shows that the artifact-level audit was checking the wrong boundary.
"""
    (out_dir / "REPORT.md").write_text(report, encoding="utf-8")

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
