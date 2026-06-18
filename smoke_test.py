# -*- coding: utf-8 -*-
"""
main.py
~~~~~~~
Enterprise execution entrypoint to boot and run the vLLM Resilience SDK.
"""

import asyncio
import os
import sys
import logging
from unittest.mock import AsyncMock, patch
import httpx

# ==============================================================================
# FORCE GLOBAL LOGGING CONFIGURATION (Must happen before importing SDK components)
# ==============================================================================
# 1. Clear any broken default handlers
root_logger = logging.getLogger()
if root_logger.handlers:
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

# 2. Establish a high-visibility terminal logging stream handler
console_handler = logging.StreamHandler(sys.stdout)
console_formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(console_formatter)

# 3. Apply the handler globally across ALL namespaces at INFO level
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

# Now, safely import your SDK components
from src.vllm_resilience_sdk import SystemInitializationEngine
from src.vllm_resilience_sdk.clients import ProductionVLLMClient

async def start_sdk_pipeline():
    # print("=== INITIALIZING INFRASTRUCTURE BOOT SEQUENCE ===\n")
    
    # Step 1: Run your Preflight Validation Engine (Orchestrator)
    boot_orchestrator = SystemInitializationEngine(target_log_dir="./logs")
    boot_orchestrator.run_pre_boot_pipeline()
    
    # Create an INSTANCE of your client object
    client = ProductionVLLMClient()
    
    # Step 2: Initialize the connection pool using our active client instance
    await client.initialize_vllm_connection()
    
    # --------------------------------------------------------------------------
    # SIMULATION SANDBOX: Mocking the dynamic URL registry for testing locally
    # --------------------------------------------------------------------------
    mock_env = {
        "LIVE_GPU_ENDPOINT_URL": "https://api.vast.ai/v1/chat/completions",
        "VAST_AI_API_KEY": "vst_mock_production_token_7f9382bca94"
    }
    
    async def mock_aiter_lines():
        mock_data_chunks = [
            "data: {'choices': [{'delta': {'content': 'Component:'}}]}",
            "data: {'choices': [{'delta': {'content': ' Resistor R1'}}]}",
            "data: [DONE]"
        ]
        for chunk in mock_data_chunks:
            yield chunk

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.aiter_lines = mock_aiter_lines
    
    with patch.dict(os.environ, mock_env), \
         patch("httpx.AsyncClient.stream") as mock_stream:
         
        mock_stream.return_value.__aenter__.return_value = mock_response
        
        # Step 3: Dispatch an inference payload stream
        sample_payload = {
            "model": "Your llm model id",
            "messages": [{"role": "user", "content": "System integration test. Reply with the single phrase: 'CONNECTION SUCCESSFUL YOUR AI MODEL IS READY VIA `VLLM-SDK` TRANSLATER!'"}]
        }
        
        # print("\n=== STARTING ASYNC INFERENCE STREAM ===")
        
        async for token_chunk in client.send_inference_request(sample_payload):
            print(f"Stream output line received -> {token_chunk}")
            
    # print("\n=== STARTING GRACEFUL TEARDOWN SEQUENCE ===")
        await client.close_vllm_connection()
        # print("\n=== SDK SHUT DOWN CLEANLY ===")

if __name__ == "__main__":
    asyncio.run(start_sdk_pipeline())




