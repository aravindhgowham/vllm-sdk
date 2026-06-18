# vllm-sdk 
An enterprise-grade, high-performance connection manager built to connect applications safely to remote GPU servers.

## What is vllm-sdk?
When building AI applications (like chatbots, document parsers, or image text extractors), your code needs to talk to a remote GPU server. 
Writing raw network code for this is hard and can easily crash your app. The **vllm-sdk** acts as a smart, fast, and protective bridge between your apps and your AI infrastructure.


## Core Feature
    1.Asynchronous Concurrency,
    2.High-Efficiency Connection Pooling, 
    3.Thread-Safe Complexity Isolation.

## key Features & Benefits
### 1. High-Speed Live Text Streaming
* **The Old Way:** Users wait 5 to 10 seconds for the AI to completely finish thinking before seeing any text.
* **With vllm-sdk:** Text streams back instantly, word-by-word, in real-time.

### 2. Built for 100+ Shared Services
* It uses **Asynchronous Concurrency** (`asyncio`). If 100 developers use it at the same time for different projects, nobody has to wait in line.
* It uses **Connection Pooling** (`httpx`). It keeps a set of optimized "network roads" open and reuses them, saving your system from crashing under heavy traffic.

### 3. Fail-Safe Operations (Preflight Check)
* Before it even connects to the cloud, the SDK checks your environment variables and folder setups. If anything is wrong, it stops and warns you immediately.

### 4.High-Visibility Logging
* It colorizes your terminal console automatically:
  * **Cyan** for clean timestamps.
  * **Green** for successful completions `[200 OK]`.
  * **Bold Red** for infrastructure faults or errors `[404]`, `[500]`.
  * **Bold Blue** to highlight your brand identity (`vllm-sdk`) instantly.

## Quick Start for Developers
Using the SDK takes only a few lines of code inside any backend service:

```python
from vllm_resilience_sdk.logging_config import setup_sdk_logging
from vllm_resilience_sdk.clients import ProductionVLLMClient

# 1. Turn on high-visibility branded logging
setup_sdk_logging()

# 2. Start the connection client pool
client = ProductionVLLMClient()
await client.initialize_vllm_connection()

# 3. Stream your clean text response tokens natively
payload = {
    "model": "LocalModel",
    "messages": [{"role": "user", "content": "Analyze system parameters."}]
}

async for token in client.send_inference_request(payload):
    print(token, end="", flush=True)

# 4. Safely close sockets when finished
await client.close_vllm_connection()
