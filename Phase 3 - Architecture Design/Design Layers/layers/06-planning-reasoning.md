← [Back to Design Layers overview](../README.md)

# Layer 6 — Planning and Reasoning Layer

This is often missing from simple stack diagrams.

An agent needs to know:

- what the goal is
- what steps are needed
- what tools are available
- what information is missing
- when to stop
- when to ask a human
- how to recover from failure

## Planning patterns

| Pattern | Use Case |
|---|---|
| ReAct | Think-act-observe loop |
| Plan-and-execute | Multi-step business task |
| Router | Send task to correct specialist |
| Reflection | Agent reviews its own output |
| Critic model | Separate model checks answer |
| Supervisor-agent | One agent controls workers |
| State machine | Reliable enterprise workflow |
| Human-in-the-loop | Approval or missing info |

For serious enterprise use, I would not let an agent "freestyle" everything.

**Better pattern: use LLM reasoning inside controlled workflow boundaries.**

That means the architecture should define what the agent is allowed to do at each stage.
