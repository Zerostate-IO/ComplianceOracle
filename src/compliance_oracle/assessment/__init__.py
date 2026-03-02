"""Assessment module for compliance posture evaluation.

This module provides configuration, contracts, and utilities for the hybrid
deterministic/LLM assessment system.
"""

from compliance_oracle.assessment.config import (
    IntelligenceConfig,
    IntelligenceMode,
    load_intelligence_config,
)
from compliance_oracle.assessment.contracts import (
    DegradeReason,
    IntelligenceMetadata,
    IntelligenceResult,
    create_degraded_metadata,
    create_deterministic_metadata,
    create_hybrid_metadata,
)
from compliance_oracle.assessment.policy import (
    PolicyResult,
    enforce_no_fix_policy,
    sanitize_text,
)

__all__ = [
    # Config
    "IntelligenceConfig",
    "IntelligenceMode",
    "load_intelligence_config",
    # Contracts
    "DegradeReason",
    "IntelligenceMetadata",
    "IntelligenceResult",
    "create_degraded_metadata",
    "create_deterministic_metadata",
    "create_hybrid_metadata",
    # Policy
    "PolicyResult",
    "enforce_no_fix_policy",
    "sanitize_text",

# llm subpackage is available via:
# from compliance_oracle.assessment.llm import OllamaClient, OllamaResult, OllamaStatus
]
