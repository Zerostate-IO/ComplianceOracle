"""Runtime configuration for assessment intelligence hybrid mode.

This module provides configuration for the hybrid deterministic/LLM assessment
system. All settings are loaded from environment variables with sensible defaults.

Key constraint: hard_degrade is ALWAYS True - this is a core project principle.
The system will never attempt to generate remediation suggestions; it only
identifies compliance gaps.
"""

from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Type alias for intelligence mode
IntelligenceMode = Literal["deterministic", "hybrid"]


class IntelligenceConfig(BaseModel):
    """Configuration for assessment intelligence mode.

    This configuration controls how the assessment system operates:
    - deterministic: Pure rule-based assessment without LLM calls
    - hybrid: Attempts LLM-enhanced analysis with hard degrade fallback

    The hard_degrade flag is ALWAYS True and cannot be changed. This ensures
    the system never generates remediation suggestions - it only identifies gaps.
    """

    intelligence_mode: IntelligenceMode = Field(
        default="hybrid",
        description="Operating mode: 'deterministic' (rules only) or 'hybrid' (LLM with fallback)",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for Ollama API server",
    )

    ollama_model: str = Field(
        default="llama3.2",
        description="Ollama model to use for hybrid assessments",
    )

    timeout_budget_seconds: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Maximum time in seconds to wait for LLM responses",
    )

    hard_degrade: bool = Field(
        default=True,
        frozen=True,
        description="Always True - system degrades to deterministic on LLM failure",
    )

    circuit_breaker_threshold: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of consecutive failures before circuit opens",
    )

    circuit_breaker_reset_seconds: float = Field(
        default=60.0,
        ge=10.0,
        le=600.0,
        description="Seconds to wait before attempting to close circuit",
    )

    model_config = {"frozen": True}

    @field_validator("hard_degrade")
    @classmethod
    def hard_degrade_always_true(cls, v: bool) -> bool:
        """Ensure hard_degrade is always True - core project constraint."""
        if not v:
            raise ValueError(
                "hard_degrade must always be True. "
                "This system does not generate remediation suggestions."
            )
        return v


def load_intelligence_config() -> IntelligenceConfig:
    """Load intelligence configuration from environment variables.

    Environment variables:
        INTELLIGENCE_MODE: "deterministic" or "hybrid" (default: "hybrid")
        OLLAMA_BASE_URL: Ollama API endpoint (default: "http://localhost:11434")
        OLLAMA_MODEL: Model name for assessments (default: "llama3.2")
        OLLAMA_TIMEOUT_BUDGET: Timeout in seconds (default: 30.0)
        OLLAMA_CIRCUIT_BREAKER_THRESHOLD: Failure threshold (default: 3)
        OLLAMA_CIRCUIT_BREAKER_RESET: Reset timeout in seconds (default: 60.0)

    Returns:
        Frozen IntelligenceConfig instance with validated settings.

    Raises:
        ValidationError: If intelligence_mode is not a valid value.
    """
    return IntelligenceConfig(
        intelligence_mode=_get_env_str("INTELLIGENCE_MODE", "hybrid"),  # type: ignore[arg-type]
        ollama_base_url=_get_env_str("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=_get_env_str("OLLAMA_MODEL", "llama3.2"),
        timeout_budget_seconds=_get_env_float("OLLAMA_TIMEOUT_BUDGET", 30.0),
        hard_degrade=True,  # Always True - core constraint
        circuit_breaker_threshold=_get_env_int("OLLAMA_CIRCUIT_BREAKER_THRESHOLD", 3),
        circuit_breaker_reset_seconds=_get_env_float("OLLAMA_CIRCUIT_BREAKER_RESET", 60.0),
    )


def _get_env_str(key: str, default: str) -> str:
    """Get string environment variable with default."""
    value = os.environ.get(key)
    return value if value is not None else default


def _get_env_int(key: str, default: int) -> int:
    """Get integer environment variable with default."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(key: str, default: float) -> float:
    """Get float environment variable with default."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default
