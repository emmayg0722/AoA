← [Back to Design Layers overview](../README.md)

# Layer 8 — Evaluation and Testing Layer

This is one of the most underrated layers.

## Tools referenced

- LangSmith
- PromptLayer
- Ragas
- DeepEval
- Braintrust

## What you evaluate

You do not only test whether the answer "sounds good." You test:

- factual correctness
- retrieval accuracy
- citation accuracy
- tool selection
- JSON/schema validity
- latency
- cost
- safety
- robustness
- hallucination rate
- task completion rate

### For RAG agents, test:

| Metric | Meaning |
|---|---|
| Retrieval precision | Did it find relevant docs? |
| Retrieval recall | Did it miss important docs? |
| Faithfulness | Is answer grounded in source? |
| Answer relevance | Did it answer the question? |
| Citation quality | Are cited sources correct? |
| Context usage | Did it use retrieved info properly? |

### For action agents, test:

| Metric | Meaning |
|---|---|
| Tool-call accuracy | Chose the right tool |
| Argument accuracy | Passed correct parameters |
| Recovery | Handled API failure |
| Approval behavior | Asked human when required |
| Task success | Finished the business task |

Architecturally, this is non-negotiable. Without evaluation, you are demoing, not building a reliable system.
