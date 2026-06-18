# -*- coding: utf-8 -*-
import os
import asyncio
import random
import logging
import httpx
from typing import Dict, Any, AsyncGenerator, Optional, Tuple
from .ai_network_connection import AsyncNetworkStreamer
from .performance_tracking import track_stream_performance
from .exceptions import UpstreamClusterOutageException

# CRITICAL: Define the scoped namespace so the masking filter takes effect
logger = logging.getLogger("Vllm_SDK.VLLMClient")

class ProductionVLLMClient:
    # ... init and pool code ...
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize_vllm_connection(self,max_alive=30, max_connection=150, request_timeout=300.0, connection_timeout=15.0) -> None:
        """
        Args:
            max_alive:float = "maximum alive wakup connectoin",
            max_connection:int = "max connection can made",
            request_timeout:float = "Maximum time allowed for request operations (read, write, pool) after the connection is established."
            connection_timeout:float = "wait for 15 seconds for connection is establish or not. if not raise https error." 

        spawns long-lived connection pools to completely eliminate TCP/TLS handshake latency
        
        Responsible for to lookup internally,
        1. DNS Lookup
        2. TCP Connection
        3. TLS Handshake (if HTTPS)
        4. HTTP Request Sent
        5. Server Processes Request
        6. Response Received
        7. Stream Data
        """
        if not self.client:
            logger.info("VLLM server Connected! Allocating high-concurrency Keep-alive `GPU` connection pool Vllm channel....[200]")
            limits = httpx.Limits(max_keepalive_connections=max_alive, max_connections=max_connection)
            timeout = httpx.Timeout(timeout=request_timeout, connect=connection_timeout) 
            self.client = httpx.AsyncClient(limits=limits, timeout=timeout)


    async def gpu_configuration(self, env_url:Optional[str] = None,
                                env_key:Optional[str]=None) -> Tuple[str, Dict[str, str]]:
        """
        Adaptive Routing Guard: Resolves connection params directly from .env space.
        """
        # Attempt direct pull from local system environment configuration mapping
        env_url = env_url or os.environ.get("LIVE_GPU_ENDPOINT_URL")
        env_key = env_key or os.environ.get("api_key")

        if env_url and env_key:
            headers = {
                "Authorization": f"Bearer {env_key}",
                "Content-Type": "application/json"
            }
            return env_url.strip(), headers
        
        if not env_url:
            logger.critical(
                "[Configuration Failure] LIVE_GPU_ENDPOINT_URL='http://213.196.166.17:61496/v1/chat/completions' not configured....[404]"
            )
            raise RuntimeError(
                "Required environment variable LIVE_GPU_ENDPOINT_URL='http://213.196.166.17:61496/v1/chat/completions' is missing....[404]"
            )

        if not env_key:
            logger.critical(
                "[Configuration Failure] api_key='api-key' not configured.....[404]"
            )
            raise RuntimeError(
                "Required environment variable api_key='api-key' is missing......[404]"
            )




    async def close_vllm_connection(self) -> None:
        """
        Flushes active sockets safely on applicaiotn 
        """
        if self.client:
            logger.warning("Flushing client infrastructure ntwork sockets safely! Vllm connection Closed........[200]")
            await self.client.aclose()
            self.client = None


    @track_stream_performance
    async def send_inference_request(self, payload: Dict[str, Any], gpu_key:Optional[str] = None, gpu_url:Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        #Connection Resolution Priority:
        -------------------------------
        1. Explicit Parameters (Highest Priority)
            If ``gpu_url`` and ``gpu_key`` are provided, these values will be
            used directly for the request.

        2. Environment Variables (Fallback)
            If either parameter is omitted, the SDK automatically attempts to
            resolve the configuration from the process environment.

        #Required environment variables(.env):
            LIVE_GPU_ENDPOINT_URL=http://193.34.23.4:8001/v1/chat/completions
            api_key=<your-api-key>
        
        """
        if not self.client:
            raise RuntimeError("VLLM connection client requested before initialization.......[500]")

        # If this log runs in PRODUCTION, the filter automatically intercepts it 
        # and masks the 'vst_' tokens or 'base64' images inside the payload!

        MAX_RETRIES = 3
        BACKOFF_FACTOR = 3.0
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # ... connection logic ...
                target_url, target_headers = await self.gpu_configuration(env_key=gpu_key, env_url=gpu_url)

                stream_generator = AsyncNetworkStreamer.execute_raw_stream(
                    client=self.client,
                    url=target_url,
                    headers=target_headers,
                    payload=payload
                )
                logger.info(f"Network Pipeline Routed to streaming core socket on attempt {attempt}....[200 OK]")

                async for token_chunk in stream_generator:
                    yield token_chunk

                break # break the re-try logic 
            except Exception as network_anomaly:
                # Use warning level for transient, self-healing network anomalies
                logger.warning(
                    f"[GPU Link Dropped] Attempt {attempt}/{MAX_RETRIES} failed: {type(network_anomaly).__name__}. "
                    "Triggering backoff self-heal protocol..."
                )
                
                if attempt == MAX_RETRIES:
                    # Use critical level for infrastructure faults that break the request execution completely
                    logger.critical("[Infrastructure Fault] Reconnection retry budget exhausted. Aborting pipeline.")
                    raise
                
                sleep_delay = BACKOFF_FACTOR * (2 ** (attempt - 1))
                await asyncio.sleep(sleep_delay)