---
name: "browser-agent-automation"
description: "Browser automation via natural language using Playwright and LLM reasoning loop"
---

# Browser Automation Agent

Absorb browser-use patterns for agent-driven web automation.

## Core Pattern

```
Task → Agent → Browser → DOM State → Agent → Action → Browser ...
```

## Key Patterns

### 1. Structured DOM State
```python
state = await browser.get_state()
# {url, title, interactive_elements: [{index, tag, text, xpath, attrs}], viewport, screenshot}
# Agent references elements by stable INDEX, not brittle selectors
```

### 2. Minimal Action Space
```python
ACTIONS = {
    "click": {"index": int},
    "input_text": {"index": int, "text": str},
    "scroll": {"direction": "up|down", "amount": int},
    "go_to_url": {"url": str},
    "wait": {"seconds": float},
    "extract_content": {"goal": str},
}
```

### 3. Error Recovery Loop
```python
async def run_agent(task, max_steps=50):
    for _ in range(max_steps):
        state = await browser.get_state()
        action = await agent.get_next_action(state)
        try:
            result = await browser.execute_action(action)
        except Exception as e:
            # retry with error context
            continue
        if result.is_done: return result.output
```

### 4. Auth via Persistent Profile
```python
browser = Browser(config=BrowserConfig(
    user_data_dir="/path/to/chrome/profile",
))
```

## References
- https://github.com/browser-use/browser-use
- Benchmark: #1 on Odysseys (87.4%)
