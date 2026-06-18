# -*- coding: utf-8 -*-
"""
vllm_resilience_sdk.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Advanced async meta-programming decorators optimized for streaming telemetry.

:copyright: (c) 2026 by Aravindh Annadurai.
:license: MIT, see LICENSE for more details.
"""

import time
import asyncio
import logging
from functools import wraps
from typing import Any, Callable, AsyncGenerator

logger = logging.getLogger("Vllm_SDK.Performance")

def track_stream_performance(func: Callable[..., AsyncGenerator[Any, None]]) -> Callable[..., AsyncGenerator[Any, None]]:
    """
    A high-speed meta-programming decorator specifically built for Async Generators.
    Measures Time-To-First-Token (TTFT) and total stream duration without blocking the event loop.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
        start_time = time.perf_counter()
        first_token_received = False
        token_count = 0
        
        logger.debug(f"[Telemetry] Starting performance profiling for execution: {func.__name__}")

        try:
            # Execute the underlying async generator stream pool
            async for chunk in func(*args, **kwargs):
                if not first_token_received:
                    ttft = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
                    logger.info(f"[Metrics] Time-To-First-Token (TTFT): {ttft:.2f}ms")
                    first_token_received = True
                
                token_count += 1
                yield chunk  # Pass the token chunk upstream immediately with zero latency
                
        finally:
            # Calculates execution time even if the client disconnects prematurely
            total_duration = time.perf_counter() - start_time
            logger.info(
                f"[Metrics] Stream finished. Total Duration: {total_duration:.2f}s | "
                f"Chunks Processed: {token_count}"
            )

    return wrapper