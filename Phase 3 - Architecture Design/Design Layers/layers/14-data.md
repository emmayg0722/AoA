← [Back to Design Layers overview](../README.md)

# Layer 14 — Data Layer

This should be explicitly added to the stack. Agentic AI depends heavily on data architecture.

## Data sources

- documents
- databases
- APIs
- logs
- emails
- spreadsheets
- ERP tables
- CRM records
- data warehouse
- lakehouse
- knowledge base

## Data architecture questions

| Question | Why it matters |
|---|---|
| Is the data structured or unstructured? | Decides SQL/API vs RAG |
| Is it real-time or static? | Decides retrieval strategy |
| Who can access it? | Security filtering |
| Is it clean? | Output quality |
| Is it versioned? | Avoid outdated answers |
| Is there metadata? | Better search and filtering |
| Is it sensitive? | Governance needed |

For enterprise agents, data quality usually matters more than model choice.

**Bad data + great model = confident bad answer.**

> This is the same principle behind [Phase 1's Data Readiness Assessment (5C)](../../../Phase%201%20-%20Discovery%20%26%20Assessment/data-readiness-assessment-5c/README.md) — data readiness has to be judged before architecture, not after.
