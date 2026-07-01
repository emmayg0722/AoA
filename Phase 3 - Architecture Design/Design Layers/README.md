# Design Layers — An Agentic AI Architecture Reference

Phase 3 (Architecture Design) asset. This is not a tool list. Most "AI stack" diagrams answer *which tools should I use?* — but that's the wrong starting question for an AI architect. The real question is:

> **How does the agent understand, decide, act, remember, verify, and improve inside a business system?**

This reference reshapes the usual tool-collage view into 18 capability stacks / decision layers. Tools are replaceable. Architecture decisions are not.

> **Want to build one, interactively?** Open **[architecture-builder.html](architecture-builder.html)** — one comparison table across the 14 layers with real "pick one" options (upside, downside, best fit), select one option per layer like building blocks, and export a recommended architecture plan for a specific client.

## The reshaped stack

A flat view, top to bottom:

```
Business Use Case
    ↓
User Experience Layer
    ↓
Agent Orchestration Layer
    ↓
Planning / Reasoning Layer
    ↓
Tool Calling / Action Layer
    ↓
Knowledge / RAG Layer
    ↓
Data Sources / Business Systems
    ↓
Memory / State Layer
    ↓
Evaluation / Testing Layer
    ↓
Observability / Monitoring Layer
    ↓
Guardrails / Security / Governance
    ↓
Deployment / Operations
```

But governance, monitoring, and evaluation don't sit at the bottom — they wrap around everything. A more honest view:

```
        Governance / Security / Compliance
    ┌───────────────────────────────────────┐
    │ Business Use Case                     │
    │ UX / Interface                        │
    │ Agent Orchestration                   │
    │ Reasoning + Planning                  │
    │ Tools + APIs                          │
    │ RAG + Knowledge                       │
    │ Data + Business Systems               │
    │ Memory + State                        │
    │ Evaluation + Observability            │
    │ Deployment + Operations               │
    └───────────────────────────────────────┘
```

## The 18 layers

| # | Layer | What it's really about |
|---|---|---|
| 1 | [Core Intelligence](layers/01-core-intelligence.md) | Which model(s) — reasoning, cost, privacy, multimodality, compliance |
| 2 | [Agent Orchestration](layers/02-agent-orchestration.md) | State, planning, tool selection, retries, multi-agent collaboration |
| 3 | [Tool Calling / Action](layers/03-tool-calling-action.md) | How the agent executes in external systems, and what needs approval |
| 4 | [Knowledge / RAG](layers/04-knowledge-rag.md) | Retrieval, grounding, and why not everything belongs in a vector DB |
| 5 | [Memory / Context](layers/05-memory-context.md) | Session, user, task, business, and agent memory — and what *not* to remember |
| 6 | [Planning / Reasoning](layers/06-planning-reasoning.md) | ReAct, plan-and-execute, reflection, supervisor patterns |
| 7 | [Human-in-the-Loop](layers/07-human-in-the-loop.md) | When the agent must pause and ask |
| 8 | [Evaluation / Testing](layers/08-evaluation-testing.md) | Faithfulness, retrieval accuracy, tool-call accuracy, task success |
| 9 | [Observability / Monitoring](layers/09-observability-monitoring.md) | Tracing every run so failures are debuggable |
| 10 | [Guardrails / Safety](layers/10-guardrails-safety.md) | Input/output validation, injection detection, business-rule enforcement |
| 11 | [Security / Governance](layers/11-security-governance.md) | Access control, audit, model/prompt governance, compliance |
| 12 | [Deployment / Serving](layers/12-deployment-serving.md) | Where and how the agent runs in production |
| 13 | [Business Application Integration](layers/13-business-application-integration.md) | Where the agent actually creates business value (ERP, CRM, Finance...) |
| 14 | [Data](layers/14-data.md) | Structured vs. unstructured, freshness, access, quality |
| 15 | [Prompt / Instruction](layers/15-prompt-instruction.md) | Managing prompts like code — versioned, tested, reviewed |
| 16 | [Workflow / Process](layers/16-workflow-process.md) | The end-to-end agentic loop, from request to logged, evaluated result |
| 17 | [Cost / Performance](layers/17-cost-performance.md) | What drives cost, and how to control it |
| 18 | [Agent Types](layers/18-agent-types.md) | Classifying agents by role (Q&A, Document, Data, Compliance, ...) |

## Practical example: ERP Knowledge Agent

Say you're building an agent for D365 F&O consultants.

**Goal:** help consultants answer *"How do we handle this integration requirement and generate an IDD draft?"*

| Layer | Choice |
|---|---|
| UI | Teams app / internal web app |
| Model | Azure OpenAI GPT-4.1 / GPT-4o |
| Orchestration | Semantic Kernel or LangGraph |
| RAG | Azure AI Search / LlamaIndex |
| Documents | SharePoint project docs, templates |
| Structured data | D365 APIs / SQL / Dataverse |
| Memory | PostgreSQL / Redis |
| Tools | Graph API, SharePoint, D365 OData |
| Guardrails | Template validator, schema validator |
| Human approval | Consultant reviews before export |
| Evaluation | Golden test cases for IDD generation |
| Observability | App Insights / LangSmith / OpenTelemetry |
| Governance | Microsoft Purview, Entra ID permissions |
| Deployment | Azure App Service / Container Apps |

This is a real architecture, not a tool collage.

## What to remember as an AI architect

The usual "stack image" framing is roughly 70% architecture, 30% tools — but it's sharper than that:

**Tools are replaceable. Architecture decisions are not.**

The serious questions, in order:

1. What business problem does the agent solve?
2. What data does it need?
3. What actions can it take?
4. What must it never do?
5. When should it ask a human?
6. How do we know it is correct?
7. How do we debug it?
8. How do we control cost?
9. How do we secure it?
10. How does it improve over time?

When you can answer those, choosing LangGraph vs. Semantic Kernel vs. Copilot Studio becomes much easier.
