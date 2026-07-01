← [Back to Design Layers overview](../README.md)

# Layer 12 — Deployment and Serving Layer

This is how the agent actually runs.

## Tools referenced

- Streamlit
- Vercel
- Replit
- Docker
- Kubernetes

But enterprise deployment may also include:

- Azure App Service
- Azure Container Apps
- Azure Functions
- Azure Kubernetes Service
- Azure AI Foundry
- Power Platform
- Copilot Studio
- internal web apps
- Teams apps

## Deployment decisions

| Question | Options |
|---|---|
| Where does it run? | Cloud, local, hybrid |
| Who uses it? | Internal users, customers, admins |
| How is it accessed? | Web app, Teams, API, embedded ERP |
| How does it scale? | Serverless, containers, Kubernetes |
| How are secrets stored? | Key Vault / secret manager |
| How are logs stored? | App Insights / Datadog / LangSmith |
| How are versions managed? | CI/CD |

For Microsoft enterprise, a common stack could be:

**Azure AI Foundry + Azure OpenAI + Azure AI Search + Semantic Kernel/LangGraph + Microsoft Graph + Power Platform + Purview + App Insights**
