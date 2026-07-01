← [Back to Design Layers overview](../README.md)

# Layer 5 — Memory and Context Layer

This is the agent's "working memory" and "long-term memory."

## Tools referenced

- Mem0
- Zep
- Redis
- Supabase
- PostgreSQL

## Different types of memory

| Memory Type | Meaning |
|---|---|
| Session memory | What happened in this conversation |
| User memory | User preferences and recurring facts |
| Task memory | Current workflow state |
| Business memory | Past decisions, approvals, generated outputs |
| Agent memory | Lessons from previous runs |
| Cache | Fast temporary storage |

### Example

For an IDD generation agent, memory could store:

- selected template
- project name
- customer name
- missing sections
- approved wording
- source document references
- previous generated version
- human corrections

## Architect question

Should the agent remember this? Not everything should be remembered — enterprise memory needs rules.

| Data | Remember? |
|---|---|
| User prefers table-heavy output | Yes |
| Customer confidential financials | Be careful |
| Temporary uploaded document | Maybe no |
| Human approval decision | Yes |
| Hallucinated draft content | No |
| Final generated document version | Yes, with audit trail |

Memory without governance becomes risk.
