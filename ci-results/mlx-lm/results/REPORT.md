# Real MLX-LM QLoRA Distillation Case Study

## Setup

- Model: `mlx-community/Qwen2.5-0.5B-Instruct-4bit`
- Transcript-only student: QLoRA adapter trained on audited transcripts.
- Route-metadata student: QLoRA adapter trained on transcripts plus omitted `route_id`.

## Results

- Transcript-only success: 11 / 18 (0.611)
- Route-metadata success: 12 / 18 (0.667)
- Route-metadata minus transcript success: 1
- Audit budget allowed successes: 12
- Route metadata false pass under transcript audit: False

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
