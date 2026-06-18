# -*- coding: utf-8 -*-
"""
vllm_resilience_sdk.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Domain-specific exceptions for system preflight validation and cluster network faults.

:copyright: (c) 2026 by Aravindh Annadurai.
:license: MIT, see LICENSE for more details.
"""

class sdk_BaseException(Exception):
    """Base exception class for all errors raised by the SDK."""
    pass


class SystemBootValidationException(sdk_BaseException):
    """Raised when host system preflight environmental or hardware validation checks fail."""
    pass


class UpstreamClusterOutageException(sdk_BaseException):
    """Raised when all retry channels to the third-party GPU infrastructure are exhausted."""
    pass