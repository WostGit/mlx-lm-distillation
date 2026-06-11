#!/usr/bin/env python3
"""
Real MLX-LM teacher generation for PACXAI route-metadata audit.

This script:
  1. loads an actual MLX-LM model;
  2. queries it as a teacher to create transcript responses;
  3. writes two QLoRA datasets:
       - transcript_only: prompt + teacher response only
       - transcript_route: prompt + teacher response + omitted route_id
  4. writes a held-out eval set.

The route_id is intentionally omitted from transcript_only.  The paper
question is whether a student trained with route metadata recovers
hidden capability labels better than one trained from the audited
transcript alone.
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Dict, List

import mlx.core as mx
from mlx_lm import load, generate

MODEL_ID = os.environ.get("MODEL_ID", "mlx-community/Qwen2.5-0.5B-Instruct-4bit")
TRAIN_EXAMPLES = int(os.environ.get("TRAIN_EXAMPLES", "48"))
EVAL_EXAMPLES = int(os.environ.get("EVAL_EXAMPLES", "18"))
SEED = 20260610

CAPABILITIES = [
    "reasoning",
    "coding",
    "tool_use",
    "computer_use",
    "policy_edge",
    "domain_expert",
]

ROUTE_FOR_CAP = {
    "reasoning": "reasoning_route",
    "coding": "code_route",
    "tool_use": "tool_route",
    "computer_use": "computer_route",
    "policy_edge": "safety_route",
    "domain_expert": "expert_route",
}

GROUPS = ["normal", "proxy_cluster", "suspicious_campaign", "enterprise_eval"]

TASK_TEMPLATES = {
    "reasoning": [
        "Solve a short logic puzzle involving two boxes and one hidden key.",
        "Answer a multi-step arithmetic word problem about trains and timing.",
        "Explain which of three claims follows from a pair of premises.",
    ],
    "coding": [
        "Write a Python function that reverses words in a sentence.",
        "Debug a short loop that computes prefix sums.",
        "Explain why a binary search implementation may fail at boundaries.",
    ],
    "tool_use": [
        "Plan how an agent should call a weather API and then summarize the result.",
        "Describe the sequence of tool calls needed to book a calendar meeting.",
        "Given a database lookup tool, decide which query should be issued first.",
    ],
    "computer_use": [
        "Describe how to navigate a settings menu to change a privacy option.",
        "Explain steps for using a browser to compare two product pages.",
        "Plan a GUI workflow for downloading a file and moving it to a folder.",
    ],
    "policy_edge": [
        "Classify whether a borderline request should be refused or answered safely.",
        "Rewrite a risky request into a safe educational alternative.",
        "Explain a safe response strategy for a dual-use prompt.",
    ],
    "domain_expert": [
        "Summarize a clinical trial abstract at a high level without medical advice.",
        "Explain a finance risk concept using a simple example.",
        "Interpret a legal clause in plain language without giving legal advice.",
    ],
}

LABEL_LIST = ", ".join(CAPABILITIES)

def chat_prompt(tokenizer, system: str, user: str) -> str:
    messages = [
        {"role": "system", "content": system},
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

def make_population(n: int) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    idx = 0
    while len(rows) < n:
        for cap in CAPABILITIES:
            template = TASK_TEMPLATES[cap][idx % len(TASK_TEMPLATES[cap])]
            group = GROUPS[(idx * 7 + len(cap)) % len(GROUPS)]
            rows.append(
                {
                    "id": f"ex_{len(rows):04d}",
                    "capability": cap,
                    "route_id": ROUTE_FOR_CAP[cap],
                    "group": group,
                    "task_prompt": template,
                }
            )
            if len(rows) >= n:
                break
        idx += 1
    return rows

def teacher_generate(model, tokenizer, task_prompt: str) -> str:
    system = (
        "You are a concise teacher model. Answer the user's task in 2-4 short sentences. "
        "Do not mention hidden capability labels, route IDs, or metadata."
    )
    prompt = chat_prompt(tokenizer, system, task_prompt)
    text = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=80,
        verbose=False,
    )
    return str(text).strip().replace("\n", " ")

def audit_prompt(row: Dict[str, str], include_route: bool) -> str:
    base = (
        "You are auditing a transcript from a model API. "
        "Recover the hidden capability label that best explains the transcript. "
        f"Allowed labels: {LABEL_LIST}. "
        "Answer with exactly one allowed label and nothing else.\n\n"
        f"USER_TASK:\n{row['task_prompt']}\n\n"
        f"TEACHER_RESPONSE:\n{row['teacher_response']}\n"
    )

    if include_route:
        base += (
            "\nUNLOGGED_INTERNAL_METADATA_INCLUDED_FOR_THIS_STUDENT:\n"
            f"route_id={row['route_id']}\n"
        )

    return base

def chat_example(row: Dict[str, str], include_route: bool) -> Dict[str, object]:
    return {
        "messages": [
            {
                "role": "system",
                "content": "You are a strict classifier. Output one label exactly.",
            },
            {
                "role": "user",
                "content": audit_prompt(row, include_route),
            },
            {
                "role": "assistant",
                "content": row["capability"],
            },
        ]
    }

def write_jsonl(path: Path, records: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def main() -> None:
    random.seed(SEED)
    mx.random.seed(SEED)

    total = TRAIN_EXAMPLES + EVAL_EXAMPLES
    rows = make_population(total)

    print(f"Loading MLX-LM teacher/base model: {MODEL_ID}")
    model, tokenizer = load(MODEL_ID)

    for i, row in enumerate(rows):
        print(f"teacher_generation {i + 1}/{len(rows)} {row['capability']} {row['route_id']}")
        row["teacher_response"] = teacher_generate(model, tokenizer, row["task_prompt"])

    train_rows = rows[:TRAIN_EXAMPLES]
    eval_rows = rows[TRAIN_EXAMPLES:]

    transcript_train = [chat_example(r, include_route=False) for r in train_rows]
    route_train = [chat_example(r, include_route=True) for r in train_rows]

    transcript_eval = [chat_example(r, include_route=False) for r in eval_rows]
    route_eval = [chat_example(r, include_route=True) for r in eval_rows]

    write_jsonl(Path("data/mlx_lm_distill/transcript_only/train.jsonl"), transcript_train)
    write_jsonl(Path("data/mlx_lm_distill/transcript_only/valid.jsonl"), transcript_eval[: max(1, len(transcript_eval)//2)])
    write_jsonl(Path("data/mlx_lm_distill/transcript_only/test.jsonl"), transcript_eval)

    write_jsonl(Path("data/mlx_lm_distill/transcript_route/train.jsonl"), route_train)
    write_jsonl(Path("data/mlx_lm_distill/transcript_route/valid.jsonl"), route_eval[: max(1, len(route_eval)//2)])
    write_jsonl(Path("data/mlx_lm_distill/transcript_route/test.jsonl"), route_eval)

    write_jsonl(Path("data/mlx_lm_distill/eval_transcript_prompts.jsonl"), [
        {
            "id": r["id"],
            "capability": r["capability"],
            "route_id": r["route_id"],
            "group": r["group"],
            "prompt": audit_prompt(r, include_route=False),
        }
        for r in eval_rows
    ])

    write_jsonl(Path("data/mlx_lm_distill/eval_route_prompts.jsonl"), [
        {
            "id": r["id"],
            "capability": r["capability"],
            "route_id": r["route_id"],
            "group": r["group"],
            "prompt": audit_prompt(r, include_route=True),
        }
        for r in eval_rows
    ])

    write_jsonl(Path("data/mlx_lm_distill/generated_teacher_rows.jsonl"), rows)

    summary = {
        "model_id": MODEL_ID,
        "train_examples": len(train_rows),
        "eval_examples": len(eval_rows),
        "capabilities": CAPABILITIES,
    }
    Path("results/mlx_lm_distillation").mkdir(parents=True, exist_ok=True)
    Path("results/mlx_lm_distillation/data_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
