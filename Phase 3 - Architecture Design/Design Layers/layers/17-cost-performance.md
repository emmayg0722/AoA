← [Back to Design Layers overview](../README.md)

# Layer 17 — Cost and Performance Layer

Also missing from most stack diagrams, but important. Agent systems can become expensive fast.

## Cost drivers

- model choice
- token length
- number of tool calls
- retrieval volume
- reranking
- repeated reasoning loops
- long memory
- multimodal processing
- evaluation runs
- logging/tracing storage

## Control methods

| Problem | Solution |
|---|---|
| Too expensive | Model routing |
| Too slow | Cache retrieval/results |
| Too many tokens | Context compression |
| Too many failed calls | Better planning/validators |
| Too much reasoning | Use deterministic workflow |
| Large documents | Chunking + summarization |
| Repeated questions | Memory/cache |

A good architecture does not only answer correctly. It answers correctly **at acceptable cost and speed.**
