**Full Credit To LangChain**: https://academy.langchain.com/

```
# Setup your .env
GEMINI_KEY=
MODEL_CHOICE=gemini-2.0-flash

TAVILY_API_KEY=
```
---
### Module-01
**Fundamental Chatbot Agent with tool-chaining using Langchain**
```
📁  module-01
│
├── agents/
│   └── __init__.py       # 🧠 Initializing Agent
│   └── agent.py
├── config/
│   └── settings.py       # 🔧 Environment configuration & Agent setting
├── tools/
│   └── __init__.py       # 📋 Tools for agent
│   └── tools.py
└── main.py 
```
---
### Module-02
**Chabot with memory using Langchain + Langgraph**
```
📁  module-02
│
├── sqlite_db/
│    └── example.db                # 🧠 Long term memory storate
├── long_term_memory_chatbot.py    # 🤖 Chatbot with persistant memory (sqlite)
│
└── short_term_memory_chatbot.py   # 🤖 Chatbot with temporary memory (MemorySaver)
```
---
### Module-03
**ToDo Assistant (MemoryStore)**
* **from langgraph.store.base import BaseStore**
  * BaseStore is an abstract interface that defines the contract for storage operations
  * Provides methods like put(), get(), search(), and delete()
* **from langgraph.store.memory import InMemoryStore**
  * InMemoryStore is a concrete implementation of BaseStore
  * Stores data in RAM (memory) during the application session

![Graph](.module-03\module-3.png)
```
📁  module-03
├── config.py          # Configuration and LLM setup
├── schemas.py         # Pydantic models and data structures
├── utils.py           # Helper functions and utilities
├── prompts.py         # All prompt templates
├── nodes.py           # Graph node functions
├── graph.py           # Graph construction
└── main.py            # Entry point
```
---
### Module-04
**Research assistant (Parallel workflow + subgraph)**
* Workflow
  * Topic Input → Create specialized analysts
  * Human Review → Approve/modify analysts (with interruption)
  * Parallel Interviews → Each analyst conducts focused research
  * Section Writing → Convert interviews to report sections
  * Report Assembly → Combine into final formatted report

![Graph](.module-04\module-4.png)
```
📁  module-04
├── __init__.py
├── config.py
├── models.py
├── nodes/
│   ├── __init__.py
│   ├── analyst_nodes.py
│   ├── interview_nodes.py
│   └── report_nodes.py
├── graphs/
│   ├── __init__.py
│   ├── interview_graph.py
│   └── research_graph.py
└── main.py
```
---
