← [Back to Design Layers overview](../README.md)

# Layer 9 — Observability and Monitoring Layer

This is the "what happened?" layer.

## Tools referenced

- Helicone
- Arize AI
- Datadog
- OpenTelemetry
- LangSmith-style tracing

## What should be monitored

For every agent run, you want to know:

- user input
- retrieved documents
- model used
- prompt version
- tool calls
- tool outputs
- errors
- latency
- token usage
- cost
- final answer
- human approvals
- security events

## Why this matters

When a user says: *"The agent generated the wrong IDD section,"* you need to trace:

1. Which template did it use?
2. Which source document did it read?
3. What prompt version was used?
4. Did retrieval fail?
5. Did the model ignore instructions?
6. Was the section missing from the input?
7. Did the post-validator catch it?

No tracing = no debugging.
