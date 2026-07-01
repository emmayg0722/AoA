← [Back to Design Layers overview](../README.md)

# Layer 11 — Security and Governance Layer

This is where enterprise AI becomes serious.

## Tools referenced

- Credo AI
- Holistic AI
- Microsoft Purview
- Protect AI
- OpenMetadata

## Key areas

| Area | Meaning |
|---|---|
| Access control | User can only access allowed data |
| Data classification | Public/internal/confidential/restricted |
| Audit logs | Record what agent did |
| Model governance | Which model is allowed for which data |
| Prompt governance | Approved prompt versions |
| Tool permissions | Which actions can be executed |
| Compliance | GDPR, EU AI Act, internal policies |
| Data retention | How long logs/memory are stored |
| Human accountability | Who approved what |

## Architect question

Can this agent access sensitive company or customer data? If yes, you need governance from day one.

A common enterprise pattern: **agent identity + user identity + permission filtering.**

The agent should not become a superuser. It should act under the user's permissions or a tightly scoped service identity.
