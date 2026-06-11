# Assumption Bug Demonstration

The audit claims:

```text
Student = train(Transcript)
```

But the real pipeline may be:

```text
Student = train(Transcript, RouteMetadata)
```

The MLX experiment demonstrates that this omitted input can produce a false pass:
the transcript simulator remains under budget while the route-metadata student exceeds it.
