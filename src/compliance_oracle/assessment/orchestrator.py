"""Deterministic-first hybrid intelligence orchestrator.

This module provides the IntelligenceOrchestrator that executes deterministic
scoring first, then optional LLM enrichment. On client error/timeout/circuit-open,
it returns deterministic results with stable shape and metadata.

Design principles:
- Deterministic assessment ALWAYS runs first
- Control status and gap detection are ALWAYS from deterministic logic
- LLM can only add enrichment text (rationale, context)
- LLM can NEVER change control status or severity
- Hard-degrade on any LLM failure (no exceptions escape)
- All errors captured in metadata for audit trail
"""

from __future__ import annotations

import time
from typing import Any, Literal

from pydantic import BaseModel, Field

from compliance_oracle.assessment.config import IntelligenceConfig
from compliance_oracle.assessment.contracts import (
    DegradeReason,
    IntelligenceMetadata,
    create_degraded_metadata,
    create_deterministic_metadata,
    create_hybrid_metadata,
)
from compliance_oracle.assessment.llm.ollama_client import OllamaClient, OllamaResult
from compliance_oracle.assessment.policy import PolicyResult, enforce_no_fix_policy


class OrchestratorResult(BaseModel):
    """Result from the IntelligenceOrchestrator.

    This model contains all deterministic assessment fields plus metadata
    describing how the result was produced. Deterministic fields are ALWAYS
    populated; enrichment fields are only populated when LLM was used successfully.
    """

    # Core deterministic fields - ALWAYS populated
    control_id: str = Field(description="Control identifier (e.g., 'PR.AC-01')")
    control_name: str = Field(description="Control name from framework")
    framework_id: str = Field(description="Framework identifier")
    maturity_level: str = Field(
        description="Assessed maturity level: basic, intermediate, advanced, or not_addressed"
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Areas where implementation is strong (from deterministic analysis)",
    )
    gaps: list[str] = Field(
        default_factory=list,
        description="Identified gaps in implementation (from deterministic analysis)",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Gap-focused observations (never prescriptive fixes)",
    )

    # Optional LLM enrichment fields
    llm_rationale: str | None = Field(
        default=None,
        description="LLM-generated rationale for the assessment (when available)",
    )
    llm_context: str | None = Field(
        default=None,
        description="Additional context from LLM analysis (when available)",
    )

    # Metadata describing the analysis mode
    metadata: IntelligenceMetadata = Field(
        default_factory=lambda: IntelligenceMetadata(),
        description="Metadata describing the analysis mode and any degradation events",
    )

    @property
    def is_llm_used(self) -> bool:
        """Check if LLM was used in producing this result."""
        return self.metadata.llm_used

    @property
    def degrade_reason(self) -> DegradeReason | None:
        """Get the degradation reason, if any."""
        return self.metadata.degrade_reason

    @property
    def has_policy_violations(self) -> bool:
        """Check if any policy violations were detected."""
        return len(self.metadata.policy_violations) > 0


class EvaluationOrchestratorResult(BaseModel):
    """Result from the IntelligenceOrchestrator for bulk evaluation.

    This model contains findings from bulk evaluation plus metadata.
    """

    # Core deterministic fields
    findings: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of compliance findings from deterministic analysis",
    )
    evaluated_controls_count: int = Field(
        default=0,
        description="Number of controls evaluated",
    )
    compliant_areas: list[str] = Field(
        default_factory=list,
        description="Areas found to be compliant",
    )

    # Optional LLM enrichment
    llm_summary: str | None = Field(
        default=None,
        description="LLM-generated summary of findings (when available)",
    )

    # Metadata
    metadata: IntelligenceMetadata = Field(
        description="Metadata describing the analysis mode and any degradation events",
    )

    @property
    def is_llm_used(self) -> bool:
        """Check if LLM was used in producing this result."""
        return self.metadata.llm_used

    @property
    def degrade_reason(self) -> DegradeReason | None:
        """Get the degradation reason, if any."""
        return self.metadata.degrade_reason

    @property
    def has_policy_violations(self) -> bool:
        """Check if any policy violations were detected."""
        return len(self.metadata.policy_violations) > 0

class IntelligenceOrchestrator:
    """Deterministic-first hybrid intelligence orchestrator.

    This orchestrator executes deterministic assessment first, then optionally
    enriches with LLM analysis. On any LLM failure, it gracefully degrades
    to deterministic-only results with appropriate metadata.

    The orchestrator enforces the "no-fix" policy on all LLM output.

    Example:
        config = IntelligenceConfig()
        client = OllamaClient(config)
        orchestrator = IntelligenceOrchestrator(config, client)

        result = await orchestrator.assess(
            control_id="PR.AC-01",
            response="We use MFA for all users...",
        )

        if result.is_llm_used:
            print(f"LLM rationale: {result.llm_rationale}")
        else:
            print(f"Degraded: {result.degrade_reason}")
    """

    def __init__(
        self,
        config: IntelligenceConfig,
        ollama_client: OllamaClient | None = None,
    ) -> None:
        """Initialize the orchestrator with configuration and optional Ollama client.

        Args:
            config: IntelligenceConfig with mode, timeout, and policy settings.
            ollama_client: Optional OllamaClient for LLM enrichment. If None,
                           the orchestrator operates in deterministic-only mode.
        """
        self._config = config
        self._ollama_client = ollama_client

    def _should_use_llm(self) -> bool:
        """Check if LLM enrichment should be attempted.

        Returns:
            True if mode is hybrid AND Ollama client is available.
        """
        return self._config.intelligence_mode == "hybrid" and self._ollama_client is not None

    def _run_deterministic_assessment(
        self,
        control_id: str,
        response: str,
    ) -> dict[str, Any]:
        """Run deterministic assessment logic.

        This method extracts maturity level, strengths, and gaps from the response
        using purely rule-based analysis.

        Args:
            control_id: The control being assessed.
            response: User's response describing their implementation.

        Returns:
            Dict with deterministic assessment results:
            - control_id, control_name, framework_id
            - maturity_level
            - strengths, gaps, recommendations
        """
        # Import deterministic functions from assessment tools
        from compliance_oracle.tools.assessment import (
            _assess_maturity_level,
            _generate_recommendations,
            _get_category_from_control_id,
            _identify_gaps,
            _identify_strengths,
        )

        # Run deterministic analysis
        maturity = _assess_maturity_level(response, control_id)
        strengths = _identify_strengths(response)
        gaps = _identify_gaps(response, control_id, maturity)
        recommendations = _generate_recommendations(gaps, maturity)

        # Extract control name from control_id (simplified)
        category = _get_category_from_control_id(control_id)
        control_name = f"Control {control_id}"

        return {
            "control_id": control_id,
            "control_name": control_name,
            "framework_id": "nist-csf-2.0",  # Default framework
            "maturity_level": maturity,
            "strengths": strengths,
            "gaps": gaps,
            "recommendations": recommendations,
        }

    def _run_deterministic_evaluation(
        self,
        content: str,
        content_type: str,
        controls: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Run deterministic evaluation logic.

        This method evaluates content against a list of controls using
        purely rule-based analysis.

        Args:
            content: Content to evaluate.
            content_type: Type of content (POLICY, PROCEDURE, etc.).
            controls: List of control dicts to evaluate against.

        Returns:
            Dict with deterministic evaluation results:
            - findings: List of ComplianceFinding dicts
            - evaluated_controls_count
            - compliant_areas
        """
        content_lower = content.lower()
        findings: list[dict[str, Any]] = []
        compliant_areas: list[str] = []

        # Simple heuristic: check for common compliance indicators
        compliance_keywords = {
            "PR.AC": ["mfa", "multi-factor", "sso", "single sign-on", "authentication"],
            "PR.DS": ["encryption", "encrypted", "tls", "ssl", "data protection"],
            "PR.AT": ["training", "awareness", "education", "security culture"],
            "PR.IP": ["patch", "vulnerability", "update", "change management"],
            "DE.CM": ["monitoring", "siem", "logging", "detection", "alerting"],
        }

        for control in controls:
            control_id = control.get("id", "")
            category_prefix = control_id.split("-")[0] if "-" in control_id else control_id

            keywords = compliance_keywords.get(category_prefix, [])
            has_indicator = any(kw in content_lower for kw in keywords)

            if has_indicator:
                if category_prefix not in compliant_areas:
                    compliant_areas.append(category_prefix)
            else:
                # Potential gap
                findings.append(
                    {
                        "control_id": control_id,
                        "control_name": control.get("name", f"Control {control_id}"),
                        "function": control.get("function_name", "Unknown"),
                        "category": control.get("category_name", "Unknown"),
                        "finding": f"No evidence of {control.get('name', control_id)} coverage",
                        "rationale": "Content does not demonstrate coverage of this control",
                        "severity": "medium",
                    }
                )

        return {
            "findings": findings,
            "evaluated_controls_count": len(controls),
            "compliant_areas": compliant_areas,
        }

    async def _enrich_with_llm(
        self,
        prompt: str,
    ) -> tuple[str | None, OllamaResult | None]:
        """Attempt LLM enrichment with timeout and error handling.

        This method calls the Ollama client with the given prompt and handles
        all errors gracefully. It never raises exceptions.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            Tuple of (enriched_text, ollama_result):
            - enriched_text: The LLM response text, or None on failure
            - ollama_result: The full OllamaResult with status and error info
        """
        if self._ollama_client is None:
            return None, None

        try:
            result = await self._ollama_client.generate(prompt)

            if result.status == "ok" and result.content:
                return result.content, result
            else:
                return None, result

        except Exception:
            # Catch any unexpected exceptions and return degraded result
            return None, OllamaResult(
                status="error",
                error_code=DegradeReason.OLLAMA_UNREACHABLE,
                latency_ms=0,
            )

    def _build_assessment_prompt(
        self,
        control_id: str,
        response: str,
        deterministic_result: dict[str, Any],
    ) -> str:
        """Build a prompt for LLM enrichment.

        The prompt asks for rationale and context WITHOUT changing the
        deterministic assessment.

        Args:
            control_id: The control being assessed.
            response: User's response.
            deterministic_result: The deterministic assessment result.

        Returns:
            Prompt string for LLM.
        """
        maturity = deterministic_result.get("maturity_level", "unknown")
        gaps = deterministic_result.get("gaps", [])
        strengths = deterministic_result.get("strengths", [])

        return f"""You are a compliance analyst. A user has provided the following response for control {control_id}:

Response: {response}

Deterministic analysis has already determined:
- Maturity level: {maturity}
- Strengths: {", ".join(strengths) if strengths else "None identified"}
- Gaps: {", ".join(gaps) if gaps else "None identified"}

Provide a brief rationale explaining WHY this maturity level was assigned, and any additional context about the assessment.

IMPORTANT:
- Do NOT suggest fixes or remediation steps
- Do NOT recommend implementing specific controls
- Only explain the current state and gaps identified
- Focus on gap identification, not solutions

Format your response as:
Rationale: <explanation of maturity level>
Context: <any additional relevant context>"""

    async def assess(
        self,
        control_id: str,
        response: str,
        context: dict[str, Any] | None = None,
    ) -> OrchestratorResult:
        """Assess a control response with deterministic-first hybrid analysis.

        This method:
        1. Runs deterministic assessment FIRST (always)
        2. If hybrid mode and LLM available, attempts enrichment
        3. Applies policy guard to LLM output
        4. Returns result with appropriate metadata

        Args:
            control_id: The control being assessed (e.g., "PR.AC-01").
            response: User's response describing their implementation.
            context: Optional context dict with additional info.

        Returns:
            OrchestratorResult with deterministic assessment and optional
            LLM enrichment. Never raises exceptions.
        """
        start_time = time.monotonic()

        # Step 1: Run deterministic assessment FIRST (always)
        deterministic_result = self._run_deterministic_assessment(control_id, response)

        # Override with context if provided
        if context:
            if "control_name" in context:
                deterministic_result["control_name"] = context["control_name"]
            if "framework_id" in context:
                deterministic_result["framework_id"] = context["framework_id"]

        # Step 2: Check if we should attempt LLM enrichment
        if not self._should_use_llm():
            latency_ms = int((time.monotonic() - start_time) * 1000)
            return OrchestratorResult(
                **deterministic_result,
                metadata=create_deterministic_metadata(latency_ms=latency_ms),
            )

        # Step 3: Attempt LLM enrichment
        prompt = self._build_assessment_prompt(control_id, response, deterministic_result)
        llm_output, ollama_result = await self._enrich_with_llm(prompt)

        latency_ms = int((time.monotonic() - start_time) * 1000)

        # Step 4: Handle LLM failure/degradation
        if ollama_result is None or ollama_result.status != "ok":
            degrade_reason = (
                ollama_result.error_code if ollama_result else DegradeReason.OLLAMA_UNREACHABLE
            )
            return OrchestratorResult(
                **deterministic_result,
                metadata=create_degraded_metadata(
                    degrade_reason=degrade_reason,
                    latency_ms=latency_ms,
                ),
            )

        # Step 5: Apply policy guard to LLM output
        policy_result = enforce_no_fix_policy(llm_output or "")

        # Step 6: Extract enrichment from LLM output
        llm_rationale = None
        llm_context = None

        if policy_result.sanitized_text:
            # Parse the structured response
            text = policy_result.sanitized_text
            if "Rationale:" in text:
                parts = text.split("Context:")
                rationale_part = parts[0].replace("Rationale:", "").strip()
                llm_rationale = rationale_part
                if len(parts) > 1:
                    llm_context = parts[1].strip()
            else:
                # Fallback: use entire text as rationale
                llm_rationale = text

        # Step 7: Build final result with enrichment
        policy_violations = policy_result.violations if policy_result.policy_violation else []

        return OrchestratorResult(
            **deterministic_result,
            llm_rationale=llm_rationale,
            llm_context=llm_context,
            metadata=create_hybrid_metadata(
                llm_used=True,
                policy_violations=policy_violations if policy_violations else None,
                latency_ms=latency_ms,
            ),
        )

    async def evaluate(
        self,
        content: str,
        content_type: str,
        controls: list[dict[str, Any]],
    ) -> EvaluationOrchestratorResult:
        """Evaluate content against controls with deterministic-first hybrid analysis.

        This method:
        1. Runs deterministic evaluation FIRST (always)
        2. If hybrid mode and LLM available, attempts summary enrichment
        3. Applies policy guard to LLM output
        4. Returns result with appropriate metadata

        Args:
            content: Content to evaluate.
            content_type: Type of content (POLICY, PROCEDURE, etc.).
            controls: List of control dicts to evaluate against.

        Returns:
            EvaluationOrchestratorResult with deterministic findings and optional
            LLM summary. Never raises exceptions.
        """
        start_time = time.monotonic()

        # Step 1: Run deterministic evaluation FIRST (always)
        deterministic_result = self._run_deterministic_evaluation(content, content_type, controls)

        # Step 2: Check if we should attempt LLM enrichment
        if not self._should_use_llm():
            latency_ms = int((time.monotonic() - start_time) * 1000)
            return EvaluationOrchestratorResult(
                **deterministic_result,
                metadata=create_deterministic_metadata(latency_ms=latency_ms),
            )

        # Step 3: Build prompt for LLM summary
        findings_count = len(deterministic_result["findings"])
        prompt = f"""You are a compliance analyst. A deterministic evaluation has identified {findings_count} potential compliance gaps.

Compliant areas: {", ".join(deterministic_result["compliant_areas"]) or "None identified"}
Gap areas: {findings_count} controls with potential gaps

Provide a brief summary of the compliance posture based on these findings.

IMPORTANT:
- Do NOT suggest fixes or remediation steps
- Do NOT recommend implementing specific controls
- Only summarize the current state and gaps identified
- Focus on gap identification, not solutions

Summary:"""

        # Step 4: Attempt LLM enrichment
        llm_output, ollama_result = await self._enrich_with_llm(prompt)

        latency_ms = int((time.monotonic() - start_time) * 1000)

        # Step 5: Handle LLM failure/degradation
        if ollama_result is None or ollama_result.status != "ok":
            degrade_reason = (
                ollama_result.error_code if ollama_result else DegradeReason.OLLAMA_UNREACHABLE
            )
            return EvaluationOrchestratorResult(
                **deterministic_result,
                metadata=create_degraded_metadata(
                    degrade_reason=degrade_reason,
                    latency_ms=latency_ms,
                ),
            )

        # Step 6: Apply policy guard to LLM output
        policy_result = enforce_no_fix_policy(llm_output or "")

        # Step 7: Build final result with enrichment
        llm_summary = policy_result.sanitized_text if policy_result.sanitized_text else None
        policy_violations = policy_result.violations if policy_result.policy_violation else []

        return EvaluationOrchestratorResult(
            **deterministic_result,
            llm_summary=llm_summary,
            metadata=create_hybrid_metadata(
                llm_used=True,
                policy_violations=policy_violations if policy_violations else None,
                latency_ms=latency_ms,
            ),
        )
