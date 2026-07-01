← [Back to Design Layers overview](../README.md)

# Layer 1 — Core Intelligence Layer

This is the "brain" of the agent.

## What it includes

LLMs and reasoning models:

- GPT-4.1 / GPT-4o / o-series
- Claude
- Gemini
- Llama
- Mistral
- DeepSeek
- domain-specific models

## What this layer decides

This layer handles:

- reasoning
- summarization
- classification
- planning
- natural language understanding
- code generation
- business explanation
- document generation

## Architect question

Do you need:

- a general reasoning model?
- a cheap fast model?
- a private/local model?
- a multimodal model?
- a model with long context?
- a model approved by enterprise compliance?

For enterprise work, the answer is rarely "use the smartest model everywhere." That is expensive and unstable.

A better pattern is: **use different models for different jobs.**

### Example

| Task | Model Type |
|---|---|
| User conversation | Strong reasoning model |
| Document classification | Cheaper fast model |
| Embedding/search | Embedding model |
| Data extraction | Structured-output model |
| Sensitive data | Enterprise-approved model |
| Code generation | Coding-specialized model |
