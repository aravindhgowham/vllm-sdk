# -*- coding: utf-8 -*-
"""
vllm_resilience_sdk.network_core
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Low-level isolated async network streaming engine handling raw HTTPX sockets.

:copyright: (c) 2026 by Aravindh Annadurai.
:license: MIT, see LICENSE for more details.
"""

import logging
from typing import Dict, Any, AsyncGenerator
import httpx
from fastapi import status
logger = logging.getLogger("Vllm_SDK.NetworkCore")

class AsyncNetworkStreamer:
    """Handles raw isolated HTTPX stream lifecycles with zero-copy memory layouts.
    
    This file does exactly one job: it manages open connection sockets, processes response status codes, and streams lines from the network buffer. 
    It has zero knowledge of your retry budgets or your backoff limits.
    """

    @staticmethod
    async def execute_raw_stream(client: httpx.AsyncClient, url: str, headers: Dict[str, str],payload: Dict[str, Any], LiveStream: bool = True, api_method:str = "POST") -> AsyncGenerator[str, None]:
        """
        Spawns a highly isolated network stream block container.
        Allows multiple requests to safely share the root connection pool concurrently.
        """
        # Enforce stream chunking parameter across network packets
        payload["stream"] = LiveStream

        async with client.stream( method=api_method, url=url,headers=headers,json=payload) as response:
            # Intercept server faults or validation errors before streaming data
            if response.status_code != status.HTTP_200_OK:
                error_payload = await response.aread()
                raise httpx.HTTPStatusError(
                    message=f"Upstream Node Error [Status {response.status_code}]: {error_payload.decode()}",
                    request=response.request,
                    response=response
                )

            # Stream memory lines back sequentially to the request caller thread
            async for line in response.aiter_lines():
                if line.strip():
                    yield line