← [Back to Design Layers overview](../README.md)

# Layer 3 — Tool Calling and Action Layer

This is the agent's "hands."

## Tools referenced

- OpenAI function calling
- MCP
- Composio
- Pipedream
- Apify
- custom APIs

## What this layer does

It lets the agent interact with external systems:

- CRM
- ERP
- SharePoint
- Outlook
- Teams
- SQL database
- D365 F&O
- Salesforce
- Jira
- Notion
- browser/search tools
- internal APIs

Without tool calling, the agent only talks. With tool calling, the agent can execute.

## Enterprise example

For a Dynamics / ERP environment, tools might include:

| Business Action | Tool/API |
|---|---|
| Search customer | D365 API |
| Get sales order | F&O OData |
| Check inventory | ERP API |
| Read contract | SharePoint connector |
| Create support ticket | ServiceNow / Jira |
| Send email | Outlook Graph API |
| Generate report | Power BI / Fabric API |

## Architect question

Which tools are safe for the agent to call automatically, and which require approval?

| Action | Approval Needed? |
|---|---|
| Search documents | No |
| Summarize customer info | No / depends |
| Draft email | No |
| Send email | Yes |
| Update ERP record | Yes |
| Delete record | Always yes |
| Create purchase order | Yes |
| Change financial data | Strong approval |

This is where many agent projects fail: people give the agent too much action power too early.
