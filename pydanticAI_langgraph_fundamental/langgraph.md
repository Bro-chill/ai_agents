## Basic Langgraph

https://langchain-ai.github.io/langgraph/tutorials/get-started/1-build-basic-chatbot/
* **state**: 
  * State is the shared data structure that flows through entire graph
  * State persists the entire conversation history across the entire workflow
* **node**: 
  * Single unit of work/function/agent in graph
  * Essentially process the current state
* **graph**: 
  * Defines the workflow
  * How nodes connect and what order they execute
---
## Advance Langgraph

* **Add memory**:
  * Providing a checkpointer when compiling the graph and a thread_id when calling your graph, LangGraph automatically saves the state after each step.
* **Add human-in-the-loop**:
  * Allowing execution to pause and resume based on user feedback.
* **Time travel**:
  * Rewind graph by fetching a checkpoint using the graph's get_state_history.
  