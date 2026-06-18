# -*- coding: utf-8 -*-
"""
vllm-resilience-sdk
~~~~~~~~~~~~~~~~~~~
An enterprise-grade, production-hardened platform wrapper for vLLM clusters.

:copyright: (c) 2026 by Aravindh Aannadurai.
:license: MIT, see LICENSE for more details.
"""

from .clients import ProductionVLLMClient
from .validations import SystemInitializationEngine
from .exceptions import sdk_BaseException, SystemBootValidationException, UpstreamClusterOutageException
from .logging_utils import setup_sdk_logging
from .ai_network_connection import AsyncNetworkStreamer
from .performance_tracking import track_stream_performance

setup_sdk_logging()

# Authorship & Runtime Package Signatures
__version__ = "1.0.0"
__author__ = "Aravindh Annadurai"
__copyright__ = "Copyright 2026 Aravindh Annadurai"

__all__ = [
    "ProductionVLLMClient",
    "SystemInitializationEngine",
    "sdk_BaseException",
    "SystemBootValidationException",
    "UpstreamClusterOutageException",
    "AsyncNetworkStreamer",
    "track_stream_performance"
]