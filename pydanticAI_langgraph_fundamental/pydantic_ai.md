## Agent

* **deps_type** : defines external dependencies your agent needs (like API clients, database connections, API keys).
* **output_type** : specifies the structure of the agent's response.
* **system_prompt** : pre-defined instruction set that guides the model's behavior and tone throughout an interaction.
* **retries** : number of loop the agent runs
* **tools** : functions that agent can call
  * **agent.tool** : tools that need access to the agent context
  * **agent.tool_plain** : tools that don't need access to agent context
---
https://ai.pydantic.dev/api/settings/
* **model_settings** : Configure model behavior
  * **max_tokens** : Limit response length(int)
  * **temperature** : Model creativity(lower number less creative : float)
  * **top_p** : Nucleus sampling(lower number more focus and predictable : float)
  * **timeout** : Timeout for a request(second : float)
  * **presence_penalty** : Penalize new tokens if text already appeared(float)
  * **frequency_penalty** : Penalize new tokens if existing frequency in text(float)
---
https://ai.pydantic.dev/api/usage/
* **usage_limit** : Calculating usage is on the model; PydanticAI simply sums the usage information across requests.
  * **request_limit** : Max request per model(int)
  * **request_tokens_limit** : Max token request per model(int)
  * **response_tokens_limit** : Max token response per model(int)
  * **total_tokens_limit** : Max token request+response per model(int)
  * **has_token_limits** : Return (True) if token reach limit
  * **check_before_request** : Raised UsageLimitExceeded if next request would exceed request_limit
  * **check_tokens** : Raised UsageLimitExceed if usage exceeds total_tokens_limit

```python
# Agent with all the components
weather_agent = Agent(
    'openai:gpt-4o',
    deps_type=Deps,
    output_type=WeatherResponse,
    system_prompt=system_prompt,
    retries=2,
    model_settings=model_settings,
    usage_limit=usage_limit,
)
```