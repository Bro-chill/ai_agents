## Serial Agent Flow
A demonstration of serial agent architecture using Pydantic-AI to build each agent and Langgraph to orchestrate the workflow.

![Serial Flow Graph][<graph.png>]

### Agents

Fundamental structure to build an agent consist of 3 features:
- **State** : structure that helps agents pass information to each other in a clean, organized way.
- **Agent** : an AI where we can pass specific model,prompt,state,dependencies and etc.
- **Tool** : a function that allowed agent to use external systems to perform specialized tasks.

### Graph

Fundamental structure to build graph
- **State** : structure that helps agents pass information to each other in a clean, organized way.
- **Router** : to define the logic of the flow before/after each task.
- **Node** : a "node" is a function that represents a single step or action in AI workflow.
- **Graph** : orchestrate the flow from 1 node to the next.
