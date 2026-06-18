# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch

# 1. THE PRODUCTION CODE (What we want to test)
class SimpleOrchestrator:
    def check_disk(self) -> str:
        # Imagine this calls a native operating system storage check
        import os
        is_writable = os.access(".", os.W_OK) 
        
        if not is_writable:
            raise RuntimeError("Disk is locked and read-only!")
        return "Disk is healthy!"

# 2. THE PYTEST SUITE (The automated testing harness)
def test_happy_path_success():
    """Test 1: Proves that the code works cleanly under normal conditions."""
    # Setup
    orchestrator = SimpleOrchestrator()
    
    # Act
    result = orchestrator.check_disk()
    
    # Assert: Verify the output matches our exact expectation
    assert result == "Disk is healthy!"


def test_simulate_disk_failure():
    """Test 2: Proves the code catches an infrastructure crash using a mock."""
    orchestrator = SimpleOrchestrator()

    # We use 'patch' to hijack 'os.access' and force it to return False
    # This tricks our code into thinking the hard drive just crashed
    with patch("os.access", return_value=False):
        
        # Tell pytest: "The code below MUST throw a RuntimeError"
        with pytest.raises(RuntimeError) as error_context:
            orchestrator.check_disk()
        
        # Verify that the crash message is exactly what we expected
        assert "Disk is locked" in str(error_context.value)
