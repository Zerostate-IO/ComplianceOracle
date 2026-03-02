"""LLM client adapters for hybrid assessment mode.

This module provides resilient client implementations for communicating
with LLM backends (Ollama) with timeout enforcement and circuit-breaker
behavior for graceful degradation.
"""

from compliance_oracle.assessment.llm.ollama_client import (
    OllamaClient,
    OllamaResult,
    OllamaStatus,
)

__all__ = [
    "OllamaClient",
    "OllamaResult",
    "OllamaStatus",
]
