# open-vllm-sdk

[![PyPI version]](https://pypi.org/project/open-vllm-sdk/)

A high-performance, asynchronous resilience gateway client built to connect distributed application services to remote GPU infrastructure safely and efficiently. Will offers only asunchronous clients powerd by [https](https://github.com/encode/httpx)

---

## Table of Contents
1. [Overview](#-overview)
2. [Key Architecture Benefits](#-key-architecture-benefits)
3. [Installation](#-installation)
4. [Environment Configuration](#-environment-configuration)
5. [Quick Start Usage](#-quick-start-usage)
6. [Console Logging Aesthetics](#-console-logging-aesthetics)
7. [License](#-license)

---

## Overview

Managing raw HTTP streaming routes directly to high-throughput LLM clusters can cause major stability issues, such as socket exhaustion, memory crashes, or lost responses. 

The **open-vllm-sdk** wraps all this complex networking inside a clean, production-hardened interface. It handles background network management, automatically cleans up messy raw Server-Sent Event (SSE) blocks, and feeds your applications crisp, ready-to-use text tokens in real-time.


## Key Architecture Benefits
* **Asynchronous Concurrency:** Built natively on Python's `asyncio` loop. It easily supports 100+ concurrent app instances (like Chatbots, BOM Parsers, and Tender Text Extractors) without stalling performance.
* **Keep-Alive Connection Pooling:** Reuses active TCP paths over `httpx.AsyncClient` instead of spinning up new sockets for every line, cutting down **Time-To-First-Token (TTFT)**.
* **Pre-flight Integrity Checking:** Instantly scans system paths and environment flags before booting to prevent downstream configuration crashes.
* **Localized Brand Logging:** Implements highly scannable terminal tracking designed after modern web frameworks like FastAPI and Uvicorn.


## Installation
This project is fully managed using the lightning-fast `uv` Python package manager.
```python
# install from PyPI
uv add open-vllm-sdk
(or)
pip install open-vllm-sdk
```

## .env configuration
```bash
#This is your GPU custom model loaded instance & port
LIVE_GPU_ENDPOINT_URL= http://213.196.166.17:61496/v1/chat/completions
api_key='place api token or random words.' # Not mandatory-exmaple, use custom api key
```
While you can provide a apikey and live endpoint recommend above, to add
on your `.env` file.


Support for streaming responses using Server Side Events(SSE)

## Quick Start
```python
# -*- coding: utf-8 -*-

import asyncio
from dotenv import load_dotenv
from vllm_resilience_sdk.clients import ProductionVLLMClient

load_dotenv()

#run engine
async def main(sample_payload):
    # Instantiate the connection pooling client
    client = ProductionVLLMClient()
    await client.initialize_vllm_connection()
   
    #Stream processed text tokens seamlessly
    async for token in client.send_inference_request(sample_payload):
        print(token, end="", flush=True)
        yield token
    
    #Safely flush socket channels on teardown
    await client.close_vllm_connection()


#inference
import asyncio
async def test_caller():
    sample_payload = {
        "model": "Qwen/Qwen3-VL-8B-Instruct",
        "messages": [{"role": "user", "content": "What is LLM?"}],
        "max_token": 100
    }

    # Iterate over the tokens yielded by run_vllm_engine
    async for token in main(sample_payload):
        print(token, end="", flush=True)
    print("\n\n--------------")

# Run the test
asyncio.run(test_caller())

```

## Advance
### Logging 
To access the along with the logs. we used the standard lib [`logging`](https://docs.python.org/3/library/logging.html) module. 

## To Start | Example
```python
# -*- coding: utf-8 -*-
import asyncio
from dotenv import load_dotenv
from vllm_resilience_sdk.logging_utils import setup_sdk_logging
from vllm_resilience_sdk import SystemInitializationEngine
from vllm_resilience_sdk.clients import ProductionVLLMClient

load_dotenv()

async def main(sample_payload):
    #Initialize
    setup_sdk_logging()
    
    #Run background system verification checks
    verifier = SystemInitializationEngine(target_log_dir="./logs")
    verifier.run_pre_boot_pipeline()
    
    #Instantiate the connection pooling client
    client = ProductionVLLMClient()
    await client.initialize_vllm_connection()
    

    #Stream processed text tokens seamlessly
    async for token in client.send_inference_request(sample_payload):
        print(token, end="", flush=True)
        yield token
    
    #Safely flush socket channels on teardown
    await client.close_vllm_connection()

#inference
import asyncio
async def test_caller():
    sample_payload = {
        "model": "Qwen/Qwen3-VL-8B-Instruct",
        "messages": [{"role": "user", "content": "What is LLM?"}],
        "max_token": 100
    }

    # Iterate over the tokens yielded by run_vllm_engine
    async for token in main(sample_payload):
        print(token, end="", flush=True)
    print("\n\n--------------")

# Run the test
asyncio.run(test_caller())
```

> [!IMPORTANT]
`Error code as follow:`
2026-06-07 23:15:02 [WARNING] (Vllm_SDK.VLLMClient): Attempt 1/3 failed: ConnectError. Triggering backoff self-heal protocol [GPU Link Dropped]
`should check your GPU server is enbaled.`

## GPU Retried
certain gpu connection error are automatically retried 4 time by default, with a short backoff.
Connection error due to network connectivity problm, Request Timeout, Network conflict, RateLimit and internal error are reteried by default as 4.

## Connections
maximum alive wahup connection default by `30`, max connection can made by `150` default.

you can use the parameter `max_alive` & `max_conection` options to increase or decrease by `initial_vllm_connection` function.

```python
from vllm_resilience_sdk.clients import ProductionVLLMClient
client = ProductionVLLMClient()
client.initialize_vllm_connection(max_connection=0, max_alive=0)
```

you can verify the versoin that is being used at runtime with :
```py
import vllm_resilience_sdk
print(vllm_resilience_sdk.__version__)
```

