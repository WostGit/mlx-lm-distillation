# Beginner Guide

This artifact checks whether a student model is truly only post-processing of the audited transcript.

Valid:
```text
Student = train(Transcript)
```

Invalid:
```text
Student = train(Transcript, RouteMetadata)
```

The Lean proof checks the valid case. The MLX experiment shows the invalid case creates a measurable recovery lift.
