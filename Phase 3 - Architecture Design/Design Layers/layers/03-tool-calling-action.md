← [Back to Design Layers overview](../README.md)

# Layer 3 — Tool Calling and Action Layer

This is the agent's "hands."

## Tools referenced

- function calling (OpenAI, Anthropic, and every major provider)
- MCP (Model Context Protocol)
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

## What MCP changed

Before MCP, every agent framework had its own way of describing a tool, so an
integration written for one agent had to be rewritten for the next. MCP is an
open protocol for exposing tools, data sources and prompts to any agent that
speaks it.

For an architect that matters in three practical ways:

- **Integrations become reusable.** An MCP server for your ERP works with any
  MCP-capable agent, not just the one you built it for. That changes build-vs-buy
  maths for connectors.
- **The trust boundary gets a name.** An MCP server is where you decide what the
  agent may see and do — a single place to enforce permissions, rather than
  scattering checks through prompt text.
- **It does not remove the approval question below.** A protocol makes an action
  easy to call; it does not make it safe to call unattended.

Client-side, most vendors now ship MCP support. If you are choosing an
orchestration framework, whether it speaks MCP is a reasonable filter.

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
