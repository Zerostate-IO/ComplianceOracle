"""Policy guard for enforcing no-fix output principle.

This module provides deterministic checks and sanitization for forbidden
remediation/recommendation patterns. It enforces the core project principle:
"Identify what isn't compliant and why. Never suggest fixes."

Design principles:
- Regex-only pattern matching (no NLP/ML dependencies)
- Detect and flag violations, with optional sanitization
- Preserve legitimate gap-identification language
- Structured results for programmatic handling
"""

import re
from typing import Final

from pydantic import BaseModel, Field


class PolicyResult(BaseModel):
    """Result of policy enforcement on text.

    Contains the original text, sanitized version (if applicable),
    whether a violation was detected, and the list of matched forbidden phrases.
    """

    original_text: str = Field(description="The original text before policy enforcement")
    sanitized_text: str = Field(
        description="The text after sanitization (may be same as original if no violations)"
    )
    policy_violation: bool = Field(description="Whether any forbidden patterns were detected")
    violations: list[str] = Field(
        default_factory=list,
        description="List of matched forbidden phrases that triggered the violation",
    )


# Pattern categories for forbidden remediation language

# Imperative recommendations: "should implement", "must deploy", etc.
_IMPERATIVE_RECOMMENDATION_PATTERNS: Final[list[str]] = [
    r"\bshould\s+implement\b",
    r"\bshould\s+deploy\b",
    r"\bshould\s+configure\b",
    r"\bshould\s+install\b",
    r"\bshould\s+enable\b",
    r"\bshould\s+set\s+up\b",
    r"\bshould\s+add\b",
    r"\bshould\s+create\b",
    r"\bshould\s+establish\b",
    r"\bshould\s+enable\b",
    r"\bshould\s+update\b",
    r"\bshould\s+upgrade\b",
    r"\bshould\s+patch\b",
    r"\bmust\s+implement\b",
    r"\bmust\s+deploy\b",
    r"\bmust\s+configure\b",
    r"\bmust\s+install\b",
    r"\bmust\s+enable\b",
    r"\bmust\s+set\s+up\b",
    r"\bmust\s+add\b",
    r"\bmust\s+create\b",
    r"\bmust\s+establish\b",
    r"\bmust\s+update\b",
    r"\bmust\s+upgrade\b",
    r"\bmust\s+patch\b",
    r"\bneed\s+to\s+implement\b",
    r"\bneed\s+to\s+deploy\b",
    r"\bneed\s+to\s+configure\b",
    r"\bneed\s+to\s+install\b",
    r"\bneed\s+to\s+enable\b",
    r"\bneeds\s+to\s+be\s+implemented\b",
    r"\bneeds\s+to\s+be\s+deployed\b",
    r"\bneeds\s+to\s+be\s+configured\b",
    r"\bneeds\s+to\s+be\s+installed\b",
    r"\bneeds\s+to\s+be\s+enabled\b",
]

# Prescriptive language: "we recommend", "it is recommended"
_PRESCRIPTIVE_PATTERNS: Final[list[str]] = [
    r"\bwe\s+recommend\b",
    r"\bi\s+recommend\b",
    r"\bit\s+is\s+recommended\b",
    r"\brecommend\s+implementing\b",
    r"\brecommend\s+deploying\b",
    r"\brecommend\s+configuring\b",
    r"\brecommend\s+installing\b",
    r"\brecommend\s+enabling\b",
    r"\brecommend\s+setting\s+up\b",
    r"\brecommend\s+adding\b",
    r"\brecommend\s+creating\b",
    r"\brecommend\s+establishing\b",
    r"\brecommend\s+updating\b",
    r"\brecommend\s+upgrading\b",
    r"\brecommend\s+patching\b",
    r"\brecommended\s+to\s+implement\b",
    r"\brecommended\s+to\s+deploy\b",
    r"\brecommended\s+to\s+configure\b",
    r"\brecommended\s+to\s+install\b",
    r"\brecommended\s+to\s+enable\b",
]

# Direct second-person recommendations
_SECOND_PERSON_PATTERNS: Final[list[str]] = [
    r"\byou\s+should\b",
    r"\byou\s+must\b",
    r"\byou\s+need\s+to\b",
    r"\byou\s+are\s+advised\s+to\b",
    r"\byou\s+are\s+required\s+to\b",
    r"\byour\s+organization\s+should\b",
    r"\byour\s+team\s+should\b",
]

# Fix-oriented verbs in advice context
_FIX_ORIENTED_PATTERNS: Final[list[str]] = [
    r"\bto\s+fix\s+this\b",
    r"\bto\s+address\s+this\s+gap\b",
    r"\bto\s+resolve\s+this\b",
    r"\bto\s+remediate\b",
    r"\bremediation\s+step\b",
    r"\bremediation\s+action\b",
    r"\bfix\s+the\s+issue\b",
    r"\bresolve\s+the\s+issue\b",
    r"\baddress\s+the\s+gap\b",
]

# Solution prescriptive patterns
_SOLUTION_PATTERNS: Final[list[str]] = [
    r"\bthe\s+solution\s+is\b",
    r"\ba\s+solution\s+would\s+be\b",
    r"\bone\s+approach\s+is\s+to\b",
    r"\bconsider\s+implementing\b",
    r"\bconsider\s+deploying\b",
    r"\bconsider\s+using\b",
    r"\bconsider\s+enabling\b",
]

# Combine all patterns and compile them once
_ALL_PATTERN_STRINGS: Final[list[str]] = (
    _IMPERATIVE_RECOMMENDATION_PATTERNS
    + _PRESCRIPTIVE_PATTERNS
    + _SECOND_PERSON_PATTERNS
    + _FIX_ORIENTED_PATTERNS
    + _SOLUTION_PATTERNS
)

FORBIDDEN_PATTERNS: Final[list[re.Pattern[str]]] = [
    re.compile(pattern, re.IGNORECASE) for pattern in _ALL_PATTERN_STRINGS
]

# Mapping from pattern string to suggested replacement for sanitization
_SANITIZATION_REPLACEMENTS: Final[dict[str, str]] = {
    # Imperative recommendations -> gap-focused language
    r"\bshould\s+implement\b": "implementation of",
    r"\bshould\s+deploy\b": "deployment of",
    r"\bshould\s+configure\b": "configuration of",
    r"\bshould\s+install\b": "installation of",
    r"\bshould\s+enable\b": "enabling of",
    r"\bmust\s+implement\b": "implementation of",
    r"\bmust\s+deploy\b": "deployment of",
    r"\bmust\s+configure\b": "configuration of",
    r"\bmust\s+install\b": "installation of",
    r"\bmust\s+enable\b": "enabling of",
    # Prescriptive language -> neutral observation
    r"\bwe\s+recommend\b": "note:",
    r"\bi\s+recommend\b": "note:",
    r"\bit\s+is\s+recommended\b": "it may be beneficial to consider",
    # Second person -> passive/neutral
    r"\byou\s+should\b": "it would be appropriate to",
    r"\byou\s+must\b": "it is necessary to",
    r"\byou\s+need\s+to\b": "there is a need to",
    # Fix-oriented -> gap-focused
    r"\bto\s+fix\s+this\b": "regarding this gap",
    r"\bto\s+address\s+this\s+gap\b": "this gap indicates",
    r"\bto\s+resolve\s+this\b": "this issue indicates",
    r"\bto\s+remediate\b": "remediation of",
    # Solution patterns -> neutral
    r"\bthe\s+solution\s+is\b": "a potential consideration is",
    r"\bconsider\s+implementing\b": "implementation of",
    r"\bconsider\s+deploying\b": "deployment of",
}


def _find_violations(text: str) -> list[str]:
    """Find all forbidden pattern matches in text.

    Args:
        text: The text to check for violations

    Returns:
        List of matched forbidden phrases (lowercase)
    """
    violations: list[str] = []
    for pattern in FORBIDDEN_PATTERNS:
        matches = pattern.findall(text)
        for match in matches:
            # Normalize to lowercase for consistent violation reporting
            violation = match.lower() if isinstance(match, str) else str(match).lower()
            if violation not in violations:
                violations.append(violation)
    return violations


def sanitize_text(text: str, violations: list[str]) -> str:
    """Sanitize text by replacing forbidden phrases with gap-focused language.

    This function attempts to transform remediation language into neutral,
    gap-identification language while preserving the informational content.

    Args:
        text: The original text to sanitize
        violations: List of violations to sanitize (from _find_violations)

    Returns:
        Sanitized text with forbidden phrases replaced
    """
    sanitized = text

    # Apply sanitization replacements
    for pattern_str, replacement in _SANITIZATION_REPLACEMENTS.items():
        pattern = re.compile(pattern_str, re.IGNORECASE)
        sanitized = pattern.sub(replacement, sanitized)

    return sanitized


def enforce_no_fix_policy(text: str) -> PolicyResult:
    """Enforce the no-fix policy on text.

    This function checks text for forbidden remediation language and returns
    a structured result indicating whether violations were found, what they
    were, and a sanitized version of the text.

    Args:
        text: The text to check for policy violations

    Returns:
        PolicyResult with original text, sanitized text, violation status,
        and list of violations found
    """
    if not text or not text.strip():
        return PolicyResult(
            original_text=text,
            sanitized_text=text,
            policy_violation=False,
            violations=[],
        )

    violations = _find_violations(text)

    if not violations:
        return PolicyResult(
            original_text=text,
            sanitized_text=text,
            policy_violation=False,
            violations=[],
        )

    sanitized = sanitize_text(text, violations)

    return PolicyResult(
        original_text=text,
        sanitized_text=sanitized,
        policy_violation=True,
        violations=violations,
    )
