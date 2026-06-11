# Threat Model

The protected secret is a finite hidden capability or behavior label.

The audit observes a finite transcript. The valid theorem boundary is:

```text
train : Transcript -> Student
```

The invalid hidden pipeline is:

```text
train : Transcript -> RouteMetadata -> Student
```

The MLX experiment demonstrates that omitted route metadata can create a false pass under a transcript-only audit.
