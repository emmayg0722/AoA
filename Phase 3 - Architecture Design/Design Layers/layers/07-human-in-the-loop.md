← [Back to Design Layers overview](../README.md)

# Layer 7 — Human-in-the-Loop Layer

This is essential for enterprise AI.

## Tools referenced

- Slack
- Gmail
- Airtable
- Notion
- Jira
- Linear

But the concept is bigger than tools.

## Human-in-the-loop means

The agent pauses when:

- confidence is low
- information is missing
- action is risky
- legal/compliance approval is needed
- financial data may be affected
- customer-facing output is generated

## Example approval points

For an ERP agent:

| Step | Human Needed? |
|---|---|
| Search product data | No |
| Draft customer response | Maybe |
| Send customer response | Yes |
| Update invoice | Yes |
| Recommend order quantity | Maybe |
| Create purchase order | Yes |
| Delete master data | Strong yes |

This layer protects the business from "agent went wild" scenarios.
