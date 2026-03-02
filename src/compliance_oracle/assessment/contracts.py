"""Intelligence contracts for hybrid assessment and evaluation.

This module defines the contract layer for deterministic facts, hybrid enrichment
payloads, and output metadata. These contracts support both pure deterministic
analysis and hybrid LLM-augmented evaluation modes.

Design principles:
- All fields are backward-compatible additions
- Metadata is optional to preserve existing behavior
- Degradation reasons are structured for programmatic handling
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class IntelligenceMode(StrEnum):
    """Analysis mode for assessment and evaluation operations."""

    DETERMINISTIC = "deterministic"
    HYBRID = "hybrid"


class DegradeReason(StrEnum):
    """Structured reasons for degradation from hybrid to deterministic mode.

    These codes enable programmatic handling of fallback scenarios and
    provide clear audit trails for compliance reporting.
    """

    OLLAMA_TIMEOUT = "ollama_timeout"
    OLLAMA_UNREACHABLE = "ollama_unreachable"
    OLLAMA_MALFORMED_RESPONSE = "ollama_malformed_response"
    CIRCUIT_OPEN = "circuit_open"
    POLICY_VIOLATION = "policy_violation"


class IntelligenceMetadata(BaseModel):
    """Metadata describing how an assessment or evaluation was performed.

    This model captures the analysis mode, LLM usage, and any degradation
    events that occurred during processing. It is designed to be embedded
    in result models as an optional field.
    """

    analysis_mode: IntelligenceMode = Field(
        default=IntelligenceMode.DETERMINISTIC,
        description="The analysis mode used: deterministic (rule-based) or hybrid (LLM-augmented)",
    )
    llm_used: bool = Field(
        default=False,
        description="Whether an LLM was consulted during analysis",
    )
    degrade_reason: DegradeReason | None = Field(
        default=None,
        description="If degraded from hybrid to deterministic, the reason for degradation",
    )
    policy_violations: list[str] = Field(
        default_factory=list,
        description="List of policy violations detected during LLM interaction, if any",
    )
    latency_ms: int | None = Field(
        default=None,
        description="Total processing latency in milliseconds",
    )


class IntelligenceResult(BaseModel):
    """Base result model with intelligence metadata.

    This model extends the standard result pattern with optional metadata
    that describes how the result was produced. It can be used as a base
    for assessment and evaluation results that support hybrid analysis.

    The metadata field is optional to maintain backward compatibility with
    existing result models that don't include intelligence tracking.
    """

    metadata: IntelligenceMetadata | None = Field(
        default=None,
        description="Optional metadata describing the analysis mode and any degradation events",
    )

    def get_analysis_mode(self) -> IntelligenceMode:
        """Get the effective analysis mode, defaulting to deterministic."""
        if self.metadata is None:
            return IntelligenceMode.DETERMINISTIC
        return self.metadata.analysis_mode

    def is_llm_used(self) -> bool:
        """Check if LLM was used in producing this result."""
        if self.metadata is None:
            return False
        return self.metadata.llm_used

    def get_degrade_reason(self) -> DegradeReason | None:
        """Get the degradation reason, if any."""
        if self.metadata is None:
            return None
        return self.metadata.degrade_reason

    def get_policy_violations(self) -> list[str]:
        """Get any policy violations detected during analysis."""
        if self.metadata is None:
            return []
        return self.metadata.policy_violations


def create_deterministic_metadata(
    latency_ms: int | None = None,
) -> IntelligenceMetadata:
    """Create metadata for a deterministic-only analysis.

    Args:
        latency_ms: Optional processing latency in milliseconds

    Returns:
        IntelligenceMetadata configured for deterministic mode
    """
    return IntelligenceMetadata(
        analysis_mode=IntelligenceMode.DETERMINISTIC,
        llm_used=False,
        latency_ms=latency_ms,
    )


def create_hybrid_metadata(
    llm_used: bool = True,
    degrade_reason: DegradeReason | None = None,
    policy_violations: list[str] | None = None,
    latency_ms: int | None = None,
) -> IntelligenceMetadata:
    """Create metadata for a hybrid analysis.

    Args:
        llm_used: Whether LLM was actually consulted
        degrade_reason: If degraded, the reason for degradation
        policy_violations: Any policy violations detected
        latency_ms: Optional processing latency in milliseconds

    Returns:
        IntelligenceMetadata configured for hybrid mode
    """
    return IntelligenceMetadata(
        analysis_mode=IntelligenceMode.HYBRID,
        llm_used=llm_used,
        degrade_reason=degrade_reason,
        policy_violations=policy_violations or [],
        latency_ms=latency_ms,
    )


def create_degraded_metadata(
    degrade_reason: DegradeReason,
    policy_violations: list[str] | None = None,
    latency_ms: int | None = None,
) -> IntelligenceMetadata:
    """Create metadata for a degraded hybrid analysis.

    This is a convenience function for the common case where hybrid mode
    was attempted but degraded to deterministic due to an error.

    Args:
        degrade_reason: The reason for degradation
        policy_violations: Any policy violations that caused the degradation
        latency_ms: Optional processing latency in milliseconds

    Returns:
        IntelligenceMetadata configured for degraded hybrid mode
    """
    return IntelligenceMetadata(
        analysis_mode=IntelligenceMode.HYBRID,
        llm_used=False,
        degrade_reason=degrade_reason,
        policy_violations=policy_violations or [],
        latency_ms=latency_ms,
    )
