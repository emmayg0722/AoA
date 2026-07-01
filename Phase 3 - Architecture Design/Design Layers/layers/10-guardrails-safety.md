← [Back to Design Layers overview](../README.md)

# Layer 10 — Guardrails and Safety Layer

This layer controls what the agent is allowed to say or do.

## Tools referenced

- Guardrails AI
- NeMo Guardrails
- Lakera
- Llama Guard

## Guardrails include

- input validation
- output validation
- prompt injection detection
- PII detection
- forbidden action blocking
- schema validation
- toxicity filtering
- business rule validation
- compliance checks
- source-grounding checks

## Example business guardrails

For document generation:

- Must preserve template structure.
- Must not invent missing sections.
- Must mark missing information as placeholder.
- Must cite source when using source content.
- Must not remove required headers.
- Must produce Word-compatible structure.
- Must use correct filename format: `IDD15XX`.
- Must keep document management section table-only.

This is directly relevant to a common failure mode in document-generation agents: the problem is not just prompting. You need validators.
