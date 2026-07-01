← [Back to Design Layers overview](../README.md)

# Layer 4 — Knowledge and RAG Layer

This is the agent's "company knowledge."

## Tools referenced

- LangChain
- LlamaIndex
- Haystack
- RAGFlow
- vector databases like Pinecone, Weaviate, Chroma, Qdrant, Milvus, FAISS

## What this layer does

It lets agents answer from private data:

- policy documents
- product manuals
- ERP documentation
- customer contracts
- meeting notes
- support tickets
- implementation templates
- historical projects
- SharePoint folders
- Confluence pages

## RAG is not just vector search

A mature RAG system includes:

1. Document ingestion
2. Chunking strategy
3. Metadata extraction
4. Embedding
5. Vector search
6. Keyword search
7. Hybrid retrieval
8. Reranking
9. Context compression
10. Citation generation
11. Access control
12. Freshness handling
13. Evaluation

**Simple RAG:** "Search some documents and answer."

**Production RAG:** "Search the right documents, only those the user is allowed to see, use the latest version, cite the source, and say when evidence is missing."

## Architect question

What kind of knowledge are you dealing with?

| Knowledge Type | Better Pattern |
|---|---|
| Policies/manuals | RAG |
| Structured business data | SQL/API query |
| Real-time ERP data | API tool call |
| Historical projects | RAG + metadata |
| Legal/regulatory content | RAG + citations + human review |
| Financial records | API + strict permissions |
| Document templates | RAG + structured generation |

A bad architecture mistake is putting everything into a vector DB. ERP records, prices, stock levels, customer balances — these should usually be queried from source systems, not embedded as stale text.
