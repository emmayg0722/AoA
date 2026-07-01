← [Back to Design Layers overview](../README.md)

# Layer 2 — Agent Orchestration Layer

This is where "agent" actually starts.

## Tools referenced

- LangGraph
- CrewAI
- AutoGen
- Semantic Kernel
- OpenAI Agents SDK
- LlamaIndex workflows

## What this layer does

It controls:

- agent state
- step-by-step planning
- tool selection
- retry logic
- human approval
- multi-agent collaboration
- workflow branching
- error handling

This is a major difference between a chatbot and an agent.

A chatbot answers. An agent does work.

### Example

User asks: *"Create an IDD document based on this customer requirement."*

A real agent may need to:

1. Read source documents.
2. Identify missing information.
3. Map fields to template sections.
4. Generate draft content.
5. Validate against the IDD template.
6. Ask human for missing fields.
7. Export to Word.
8. Store the output.
9. Log what was generated and why.

That is orchestration.

## Architect question

Do you need a simple flow or a stateful agent?

| Need | Better Fit |
|---|---|
| Simple Q&A | Chatbot / RAG |
| Multi-step workflow | LangGraph / Semantic Kernel |
| Microsoft-heavy enterprise | Semantic Kernel / Azure AI Foundry |
| Multi-agent experiment | CrewAI / AutoGen |
| Production reliability | LangGraph / custom orchestrator |
| No-code business users | Copilot Studio / n8n / Make |
