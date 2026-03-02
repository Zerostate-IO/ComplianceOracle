"""Assessment tools for interview-style posture building.

Provides stateless question templates that agents can use to interview
users about control implementation, then translate answers into
ControlStatus values via the existing document_compliance tool.

Also provides response evaluation for assessing user implementations
against control requirements.
"""

import re
from typing import Any

from fastmcp import FastMCP

from compliance_oracle.assessment import (
    IntelligenceConfig,
    IntelligenceOrchestrator,
)
from compliance_oracle.assessment.llm.ollama_client import OllamaClient
from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import (
    AssessmentAnswerOption,
    AssessmentAnswerType,
    AssessmentQuestion,
    AssessmentResult,
    AssessmentTemplate,
    ControlStatus,
    InterviewQuestion,
    InterviewQuestionType,
    InterviewSkipResponse,
    InterviewStartResponse,
    InterviewSubmitResponse,
    MaturityIndicators,
)

# Maturity level indicators for different control areas
MATURITY_INDICATORS: dict[str, dict[str, list[str]]] = {
    "PR.AC": {
        "basic": [
            r"password[- ]policy",
            r"access[- ]control",
            r"authentication",
        ],
        "intermediate": [
            r"multi[- ]factor",
            r"MFA",
            r"single[- ]sign[- ]on",
            r"SSO",
            r"role[- ]based",
            r"RBAC",
        ],
        "advanced": [
            r"adaptive[- ]authentication",
            r"passwordless",
            r"zero[- ]trust",
            r"identity[- ]governance",
        ],
    },
    "PR.DS": {
        "basic": [
            r"data[- ]classification",
            r"backup",
        ],
        "intermediate": [
            r"encryption[- ]at[- ]rest",
            r"encryption[- ]in[- ]transit",
            r"TLS",
            r"SSL",
            r"AES",
        ],
        "advanced": [
            r"key[- ]management",
            r"HSM",
            r"tokenization",
            r"data[- ]loss[- ]prevention",
            r"DLP",
        ],
    },
    "PR.AT": {
        "basic": [
            r"training",
            r"awareness",
        ],
        "intermediate": [
            r"security[- ]education",
            r"phishing[- ]simulation",
            r"user[- ]education",
        ],
        "advanced": [
            r"continuous[- ]learning",
            r"role[- ]based[- ]training",
            r"security[- ]culture",
        ],
    },
    "PR.IP": {
        "basic": [
            r"change[- ]management",
            r"configuration[- ]management",
        ],
        "intermediate": [
            r"vulnerability[- ]scan",
            r"patch[- ]management",
            r"hardening",
            r"baseline",
        ],
        "advanced": [
            r"continuous[- ]integration",
            r"CI/CD",
            r"infrastructure[- ]as[- ]code",
            r"IaC",
        ],
    },
    "DE.CM": {
        "basic": [
            r"monitoring",
            r"logging",
        ],
        "intermediate": [
            r"SIEM",
            r"alert",
            r"detection",
        ],
        "advanced": [
            r"anomaly[- ]detection",
            r"continuous[- ]monitoring",
            r"threat[- ]hunting",
        ],
    },
}


def _assess_maturity_level(response: str, control_id: str) -> str:
    """Assess maturity level based on response content.

    Args:
        response: User's response describing their implementation
        control_id: The control being assessed

    Returns:
        Maturity level: 'basic', 'intermediate', 'advanced', or 'not_addressed'
    """
    response_lower = response.lower()

    # Extract category from control_id (e.g., 'PR.AC' from 'PR.AC-01')
    category = "".join(control_id.split(".")[:2]) if "." in control_id else control_id
    category = f"{category[0]}.{category[1]}" if len(category) >= 2 else control_id

    indicators = MATURITY_INDICATORS.get(category, {})

    # Check for advanced indicators first
    if indicators.get("advanced"):
        for pattern in indicators["advanced"]:
            if re.search(pattern, response_lower, re.IGNORECASE):
                return "advanced"

    # Check for intermediate indicators
    if indicators.get("intermediate"):
        for pattern in indicators["intermediate"]:
            if re.search(pattern, response_lower, re.IGNORECASE):
                return "intermediate"

    # Check for basic indicators
    if indicators.get("basic"):
        for pattern in indicators["basic"]:
            if re.search(pattern, response_lower, re.IGNORECASE):
                return "basic"

    # If response is empty or very short, not addressed
    if not response or len(response.strip()) < 10:
        return "not_addressed"

    # Default to basic if any implementation is mentioned
    if any(
        word in response_lower for word in ["implement", "use", "have", "deployed", "configured"]
    ):
        return "basic"

    return "not_addressed"


def _identify_strengths(response: str) -> list[str]:
    """Identify strengths from the response.

    Args:
        response: User's response

    Returns:
        List of identified strengths
    """
    response_lower = response.lower()
    strengths: list[str] = []

    # Pattern-based strength identification
    strength_patterns = {
        "Centralized identity management": r"active[- ]directory|LDAP|identity[- ]provider|IdP",
        "Multi-factor authentication": r"multi[- ]factor|MFA|2FA|two[- ]factor",
        "Single sign-on": r"single[- ]sign[- ]on|SSO|SAML|OAuth",
        "Encryption at rest": r"encryption[- ]at[- ]rest|encrypted[- ]storage|AES",
        "Encryption in transit": r"encryption[- ]in[- ]transit|TLS|SSL|HTTPS",
        "Data classification": r"data[- ]classification|classification[- ]scheme",
        "Backup and recovery": r"backup|disaster[- ]recovery|DRP|recovery[- ]point",
        "Security monitoring": r"monitoring|SIEM|logging|detection",
        "Incident response": r"incident[- ]response|IR[- ]plan|playbook",
        "Vulnerability management": r"vulnerability[- ]scan|patch[- ]management|vulnerability[- ]assessment",
    }

    for strength_desc, pattern in strength_patterns.items():
        if re.search(pattern, response_lower, re.IGNORECASE):
            strengths.append(strength_desc)

    return strengths


def _identify_gaps(response: str, control_id: str, maturity: str) -> list[str]:
    """Identify gaps based on maturity level and response content.

    Args:
        response: User's response
        control_id: The control being assessed
        maturity: Assessed maturity level

    Returns:
        List of identified gaps
    """
    response_lower = response.lower()
    gaps: list[str] = []

    # Category-specific gap identification
    category = "".join(control_id.split(".")[:2]) if "." in control_id else control_id
    category = f"{category[0]}.{category[1]}" if len(category) >= 2 else control_id

    if category == "PR.AC":
        if maturity in ["not_addressed", "basic"]:
            gaps.append("No multi-factor authentication mentioned")
        if not re.search(r"privileged[- ]access|PAM|privilege[- ]management", response_lower):
            gaps.append("No privileged access management mentioned")
        if not re.search(r"service[- ]account|managed[- ]identity", response_lower):
            gaps.append("Service account authentication relies on static credentials")

    elif category == "PR.DS":
        if maturity in ["not_addressed", "basic"]:
            gaps.append("No encryption at rest mentioned")
        if not re.search(r"encryption[- ]in[- ]transit|TLS|SSL", response_lower):
            gaps.append("No encryption in transit mentioned")
        if not re.search(r"key[- ]management|HSM", response_lower):
            gaps.append("No key management strategy mentioned")

    elif category == "PR.AT":
        if maturity in ["not_addressed", "basic"]:
            gaps.append("No security awareness training mentioned")
        if not re.search(r"phishing[- ]simulation|security[- ]training", response_lower):
            gaps.append("No phishing simulation or advanced training mentioned")

    elif category == "PR.IP":
        if maturity in ["not_addressed", "basic"]:
            gaps.append("No vulnerability management process mentioned")
        if not re.search(r"patch[- ]management|vulnerability[- ]scan", response_lower):
            gaps.append("No patch management process mentioned")

    elif category == "DE.CM":
        if maturity in ["not_addressed", "basic"]:
            gaps.append("No continuous monitoring mentioned")
        if not re.search(r"SIEM|alert|anomaly[- ]detection", response_lower):
            gaps.append("No SIEM or centralized alerting mentioned")

    return gaps


def _generate_recommendations(gaps: list[str], maturity: str) -> list[str]:
    """Generate gap-focused recommendations.

    Args:
        gaps: Identified gaps
        maturity: Current maturity level

    Returns:
        List of recommendations (gap-focused, not prescriptive)
    """
    recommendations: list[str] = []

    # Map gaps to recommendations (identify what's missing, not how to fix it)
    gap_to_recommendation = {
        "No multi-factor authentication mentioned": "MFA coverage beyond current scope may need assessment",
        "No privileged access management mentioned": "Privileged access management controls coverage is unclear",
        "Service account authentication relies on static credentials": "Service account authentication mechanism may need review",
        "No encryption at rest mentioned": "Encryption at rest coverage needs assessment",
        "No encryption in transit mentioned": "Data in transit encryption coverage may need evaluation",
        "No key management strategy mentioned": "Key management strategy and lifecycle coverage is unclear",
        "No security awareness training mentioned": "Security awareness training program coverage may need assessment",
        "No phishing simulation or advanced training mentioned": "Advanced security training coverage may need evaluation",
        "No vulnerability management process mentioned": "Vulnerability management process coverage is unclear",
        "No patch management process mentioned": "Patch management process coverage may need assessment",
        "No continuous monitoring mentioned": "Continuous security monitoring capability may need evaluation",
        "No SIEM or centralized alerting mentioned": "Centralized security monitoring capability may need evaluation",
    }

    for gap in gaps:
        if gap in gap_to_recommendation:
            recommendations.append(gap_to_recommendation[gap])

    return recommendations


async def _evaluate_response(
    control_id: str,
    response: str,
    framework: str,
    manager: FrameworkManager,
) -> AssessmentResult:
    """Evaluate a user's response against a control.

    Args:
        control_id: The control being assessed
        response: User's response describing their implementation
        framework: Framework ID
        manager: FrameworkManager instance

    Returns:
        AssessmentResult with maturity level, strengths, gaps, and recommendations
    """
    # Get control details
    control_details = await manager.get_control_details(
        framework_id=framework,
        control_id=control_id,
    )

    if not control_details:
        return AssessmentResult(
            control_id=control_id,
            control_name="Unknown",
            framework_id=framework,
            maturity_level="not_addressed",
            strengths=[],
            gaps=["Control not found in framework"],
            recommendations=[],
        )

    # Assess maturity level
    maturity = _assess_maturity_level(response, control_id)

    # Identify strengths
    strengths = _identify_strengths(response)

    # Identify gaps
    gaps = _identify_gaps(response, control_id, maturity)

    # Generate recommendations
    recommendations = _generate_recommendations(gaps, maturity)

    return AssessmentResult(
        control_id=control_id,
        control_name=control_details.name,
        framework_id=framework,
        maturity_level=maturity,
        strengths=strengths,
        gaps=gaps,
        recommendations=recommendations,
    )


async def _get_assessment_questions_impl(
    framework: str,
    function: str | None = None,
    category: str | None = None,
    control_id: str | None = None,
) -> AssessmentTemplate:
    """Implementation of get_assessment_questions logic.

    Args:
        framework: Framework ID (e.g., "nist-csf-2.0").
        function: Optional function ID to filter controls (e.g., "PR").
        category: Optional category ID to filter controls (e.g., "PR.AC").
        control_id: Optional single control to focus on.

    Returns:
        AssessmentTemplate describing the questions to ask.
    """
    manager = FrameworkManager()

    # Determine control scope
    controls = []
    if control_id is not None:
        all_controls = await manager.list_controls(
            framework_id=framework,
            function_id=function,
            category_id=category,
        )
        controls = [c for c in all_controls if c.id == control_id]
    else:
        controls = await manager.list_controls(
            framework_id=framework,
            function_id=function,
            category_id=category,
        )

    control_ids = [c.id for c in controls]
    questions: list[AssessmentQuestion] = []

    # For now, granularity is a no-op; we always emit a single status
    # question per control.
    for ctrl in controls:
        question = AssessmentQuestion(
            id=f"{ctrl.id}-status",
            framework_id=framework,
            control_ids=[ctrl.id],
            text=(
                f"For control {ctrl.id} ({ctrl.name}), how would you rate "
                "its implementation in your environment?"
            ),
            answer_type=AssessmentAnswerType.CHOICE,
            answer_options=[
                AssessmentAnswerOption(
                    value="implemented",
                    label="Implemented",
                    maps_to_status=ControlStatus.IMPLEMENTED,
                ),
                AssessmentAnswerOption(
                    value="partial",
                    label="Partially implemented",
                    maps_to_status=ControlStatus.PARTIAL,
                ),
                AssessmentAnswerOption(
                    value="planned",
                    label="Planned",
                    maps_to_status=ControlStatus.PLANNED,
                ),
                AssessmentAnswerOption(
                    value="not_applicable",
                    label="Not applicable",
                    maps_to_status=ControlStatus.NOT_APPLICABLE,
                ),
                AssessmentAnswerOption(
                    value="not_addressed",
                    label="Not addressed",
                    maps_to_status=ControlStatus.NOT_ADDRESSED,
                ),
            ],
        )
        questions.append(question)

    # Scope metadata for the template
    scope = "framework"
    if control_id is not None:
        scope = "control"
    elif category is not None:
        scope = "category"
    elif function is not None:
        scope = "function"

    template = AssessmentTemplate(
        framework_id=framework,
        scope=scope,
        function_id=function,
        category_id=category,
        control_ids=control_ids,
        questions=questions,
    )

    return template


# --- Interview Control Helper Functions ---


INTERVIEW_QUESTIONS: dict[str, list[dict[str, Any]]] = {
    "PR.AC": [
        {
            "id": "q1",
            "question": "What authentication methods are used for user access?",
            "type": "text",
            "examples": ["Username/password", "SSO", "MFA", "Passwordless"],
        },
        {
            "id": "q2",
            "question": "Where is multi-factor authentication applied?",
            "type": "multi_select",
            "options": ["All users", "Admin accounts only", "Remote access", "Cloud services", "Not implemented"],
        },
        {
            "id": "q3",
            "question": "How are privileged accounts managed?",
            "type": "text",
            "examples": ["PAM solution", "Manual process", "Service accounts"],
        },
        {
            "id": "q4",
            "question": "Can you point to evidence of access controls?",
            "type": "evidence_link",
        },
    ],
    "PR.DS": [
        {
            "id": "q1",
            "question": "What encryption is used for data at rest?",
            "type": "text",
            "examples": ["AES-256", "BitLocker", "LUKS", "Cloud-managed keys"],
        },
        {
            "id": "q2",
            "question": "Where is encryption applied?",
            "type": "multi_select",
            "options": ["Databases", "File storage", "Backups", "Laptops/endpoints", "Cloud storage"],
        },
        {
            "id": "q3",
            "question": "How are encryption keys managed?",
            "type": "text",
            "examples": ["HSM", "Cloud KMS", "Manual key management"],
        },
        {
            "id": "q4",
            "question": "Can you point to evidence of this configuration?",
            "type": "evidence_link",
        },
    ],
    "PR.AT": [
        {
            "id": "q1",
            "question": "What security training is provided to employees?",
            "type": "text",
            "examples": ["Annual training", "Phishing simulations", "Role-based training"],
        },
        {
            "id": "q2",
            "question": "How often is training conducted?",
            "type": "multi_select",
            "options": ["Annually", "Quarterly", "Monthly", "On-demand", "Not formalized"],
        },
        {
            "id": "q3",
            "question": "How is training completion tracked?",
            "type": "text",
            "examples": ["LMS system", "Manual tracking", "HR system"],
        },
        {
            "id": "q4",
            "question": "Can you point to evidence of training programs?",
            "type": "evidence_link",
        },
    ],
    "PR.IP": [
        {
            "id": "q1",
            "question": "What vulnerability management process is in place?",
            "type": "text",
            "examples": ["Regular scans", "Patch management", "CVE monitoring"],
        },
        {
            "id": "q2",
            "question": "How are patches and updates managed?",
            "type": "multi_select",
            "options": ["Automated patching", "Manual process", "Change-controlled", "Not formalized"],
        },
        {
            "id": "q3",
            "question": "How is configuration baseline maintained?",
            "type": "text",
            "examples": ["IaC", "Configuration management tools", "Manual documentation"],
        },
        {
            "id": "q4",
            "question": "Can you point to evidence of vulnerability management?",
            "type": "evidence_link",
        },
    ],
    "DE.CM": [
        {
            "id": "q1",
            "question": "What monitoring and logging is in place?",
            "type": "text",
            "examples": ["SIEM", "Cloud-native logging", "Application monitoring"],
        },
        {
            "id": "q2",
            "question": "What is monitored?",
            "type": "multi_select",
            "options": ["Network traffic", "Application logs", "Authentication events", "Cloud resources", "Endpoints"],
        },
        {
            "id": "q3",
            "question": "How are alerts handled?",
            "type": "text",
            "examples": ["24/7 SOC", "On-call rotation", "Ticketing system"],
        },
        {
            "id": "q4",
            "question": "Can you point to evidence of monitoring configuration?",
            "type": "evidence_link",
        },
    ],
}


MATURITY_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "PR.AC": {
        "basic": "Some access controls in place, password policies defined",
        "intermediate": "MFA for critical systems, role-based access, SSO implemented",
        "advanced": "Zero-trust architecture, PAM solution, continuous access reviews",
    },
    "PR.DS": {
        "basic": "Some encryption in place, manual key management",
        "intermediate": "Encryption across most systems, centralized key management",
        "advanced": "Full encryption coverage, HSM-backed keys, automated rotation",
    },
    "PR.AT": {
        "basic": "Basic security awareness training provided",
        "intermediate": "Regular training with phishing simulations",
        "advanced": "Role-based training, continuous learning culture, metrics tracked",
    },
    "PR.IP": {
        "basic": "Basic patch management, some vulnerability scanning",
        "intermediate": "Regular scans, automated patching for most systems",
        "advanced": "CI/CD integrated scanning, IaC, automated remediation",
    },
    "DE.CM": {
        "basic": "Basic logging and monitoring in place",
        "intermediate": "SIEM deployed with alerting",
        "advanced": "Continuous monitoring, anomaly detection, threat hunting",
    },
}


def _get_category_from_control_id(control_id: str) -> str:
    """Extract category from control ID (e.g., 'PR.AC' from 'PR.AC-01')."""
    parts = control_id.split(".")
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1].split('-')[0]}"
    return control_id


def _get_interview_questions_for_category(category: str) -> list[dict[str, Any]]:
    """Get interview questions for a category."""
    # Try exact match first
    if category in INTERVIEW_QUESTIONS:
        return INTERVIEW_QUESTIONS[category]
    # Try to find a matching prefix
    for cat_key in INTERVIEW_QUESTIONS:
        if category.startswith(cat_key) or cat_key.startswith(category):
            return INTERVIEW_QUESTIONS[cat_key]
    # Return default questions for unknown categories
    return [
        {
            "id": "q1",
            "question": "Describe how this control is implemented in your environment.",
            "type": "text",
            "examples": None,
        },
        {
            "id": "q2",
            "question": "What systems or assets does this control cover?",
            "type": "text",
            "examples": None,
        },
        {
            "id": "q3",
            "question": "Can you point to evidence of this implementation?",
            "type": "evidence_link",
        },
    ]


def _get_maturity_descriptions_for_category(category: str) -> dict[str, str]:
    """Get maturity descriptions for a category."""
    if category in MATURITY_DESCRIPTIONS:
        return MATURITY_DESCRIPTIONS[category]
    for cat_key in MATURITY_DESCRIPTIONS:
        if category.startswith(cat_key) or cat_key.startswith(category):
            return MATURITY_DESCRIPTIONS[cat_key]
    return {
        "basic": "Some implementation in place",
        "intermediate": "Well-documented implementation",
        "advanced": "Mature, automated implementation",
    }


async def _interview_start(
    control_id: str,
    framework: str,
    manager: FrameworkManager,
) -> dict[str, Any]:
    """Start an interview for a control."""
    # Get control details
    control_details = await manager.get_control_details(
        framework_id=framework,
        control_id=control_id,
    )

    if not control_details:
        return {"error": f"Control {control_id} not found in framework {framework}"}

    # Get category and questions
    category = _get_category_from_control_id(control_id)
    questions_data = _get_interview_questions_for_category(category)
    maturity_desc = _get_maturity_descriptions_for_category(category)

    # Build interview questions
    questions = [
        InterviewQuestion(
            id=q["id"],
            question=q["question"],
            type=InterviewQuestionType(q["type"]),
            options=q.get("options"),
            examples=q.get("examples"),
        )
        for q in questions_data
    ]

    # Build response
    response = InterviewStartResponse(
        control_id=control_id,
        control_name=control_details.name,
        description=control_details.description,
        questions=questions,
        maturity_indicators=MaturityIndicators(**maturity_desc),
    )

    return response.model_dump()


async def _interview_submit(
    control_id: str,
    framework: str,
    answers: dict[str, str | list[str]],
    manager: FrameworkManager,
    state_manager: Any,
) -> dict[str, Any]:
    """Submit interview answers and record implementation.

    Uses the IntelligenceOrchestrator to enrich the implementation summary
    with optional LLM analysis while preserving deterministic assessment.
    """
    from compliance_oracle.models.schemas import (
        ControlDocumentation,
        Evidence,
        EvidenceType,
    )

    # Get control details
    control_details = await manager.get_control_details(
        framework_id=framework,
        control_id=control_id,
    )

    if not control_details:
        return {"error": f"Control {control_id} not found in framework {framework}"}

    # Build implementation summary from answers
    summary_parts: list[str] = []
    coverage: list[str] = []
    key_management: str | None = None
    evidence_count = 0
    evidence_items: list[Evidence] = []

    for qid, answer in answers.items():
        if qid == "q4" or "evidence" in qid.lower():
            # Handle evidence links
            if isinstance(answer, str) and answer.strip():
                evidence_items.append(
                    Evidence(
                        type=EvidenceType.OTHER,
                        path=answer,
                        description=f"Evidence provided for {control_id}",
                    )
                )
                evidence_count += 1
        elif isinstance(answer, list):
            # Multi-select answer
            if answer:
                coverage.extend(answer)
                summary_parts.append(f"Coverage: {', '.join(answer)}")
        elif isinstance(answer, str) and answer.strip():
            # Text answer
            summary_parts.append(answer)
            # Check for key management mentions
            if "key" in qid.lower() or "key" in answer.lower():
                key_management = answer

    implementation_summary = ". ".join(summary_parts) if summary_parts else "Implementation documented via interview"

    # Use orchestrator to enrich the summary with hybrid intelligence
    config = IntelligenceConfig()
    client = OllamaClient(config)
    orchestrator = IntelligenceOrchestrator(config, client)

    # Build context with control details
    context = {
        "control_name": control_details.name,
        "framework_id": framework,
    }

    # Run assessment through orchestrator for enrichment
    orchestrator_result = await orchestrator.assess(
        control_id=control_id,
        response=implementation_summary,
        context=context,
    )

    # Use orchestrator's maturity assessment (more accurate)
    maturity = orchestrator_result.maturity_level

    # Use orchestrator's strengths and gaps if available
    strengths = orchestrator_result.strengths
    gaps = orchestrator_result.gaps
    recommendations = orchestrator_result.recommendations

    # Use LLM-enriched rationale if available, otherwise use deterministic summary
    if orchestrator_result.llm_rationale:
        enriched_summary = orchestrator_result.llm_rationale
        if orchestrator_result.llm_context:
            enriched_summary += f" {orchestrator_result.llm_context}"
        implementation_summary = enriched_summary

    # Map maturity to status
    status_map = {
        "advanced": "implemented",
        "intermediate": "implemented",
        "basic": "partial",
        "not_addressed": "not_addressed",
    }
    status = status_map.get(maturity, "partial")

    # Document the control
    doc = ControlDocumentation(
        control_id=control_id,
        framework_id=framework,
        status=ControlStatus(status),
        implementation_summary=implementation_summary,
        evidence=evidence_items,
    )

    await state_manager.document_control(doc)

    # Build recorded details
    recorded: dict[str, Any] = {
        "implementation_summary": implementation_summary,
    }
    if coverage:
        recorded["coverage"] = list(set(coverage))
    if key_management:
        recorded["key_management"] = key_management
    if strengths:
        recorded["strengths"] = strengths
    if gaps:
        recorded["gaps"] = gaps

    response = InterviewSubmitResponse(
        control_id=control_id,
        status="documented",
        recorded=recorded,
        evidence_linked=evidence_count,
        assessed_maturity=maturity,
        follow_up_recommendations=recommendations,
    )

    result = response.model_dump()

    # Add metadata fields from orchestrator
    result["analysis_mode"] = orchestrator_result.metadata.analysis_mode
    result["llm_used"] = orchestrator_result.metadata.llm_used
    result["degrade_reason"] = orchestrator_result.metadata.degrade_reason

    # Add optional LLM enrichment fields if present
    if orchestrator_result.llm_rationale:
        result["llm_rationale"] = orchestrator_result.llm_rationale
    if orchestrator_result.llm_context:
        result["llm_context"] = orchestrator_result.llm_context
    if orchestrator_result.metadata.policy_violations:
        result["policy_violations"] = orchestrator_result.metadata.policy_violations
    if orchestrator_result.metadata.latency_ms is not None:
        result["latency_ms"] = orchestrator_result.metadata.latency_ms

    return result


async def _interview_skip(
    control_id: str,
    framework: str,
    state_manager: Any,
) -> dict[str, Any]:
    """Skip a control and mark as not applicable."""
    from compliance_oracle.models.schemas import ControlDocumentation

    doc = ControlDocumentation(
        control_id=control_id,
        framework_id=framework,
        status=ControlStatus.NOT_APPLICABLE,
        implementation_summary="Skipped during interview - marked as not applicable",
    )

    await state_manager.document_control(doc)

    response = InterviewSkipResponse(
        control_id=control_id,
        status="not_applicable",
        message=f"Control {control_id} marked as not applicable",
    )

    return response.model_dump()


def register_assessment_tools(mcp: FastMCP) -> None:
    """Register assessment/interview tools with the MCP server."""

    @mcp.tool()
    async def get_assessment_questions(
        framework: str = "nist-csf-2.0",
        function: str | None = None,
        category: str | None = None,
        control_id: str | None = None,
        granularity: str = "standard",  # type: ignore[unused-ignore]
    ) -> AssessmentTemplate:
        """Generate interview-style questions for assessing controls.

        This tool is intentionally stateless. It returns a set of structured
        questions that an agent can ask a human (or another system) in order
        to assess implementation status for controls in a given scope.

        The caller is expected to:
        - Ask the questions in sequence
        - Normalize the answers to the provided option values (when applicable)
        - Call document_compliance() separately to record direct status

        Args:
            framework: Framework ID (e.g., "nist-csf-2.0").
            function: Optional function ID to filter controls (e.g., "PR").
            category: Optional category ID to filter controls (e.g., "PR.AC").
            control_id: Optional single control to focus on.
            granularity: Currently reserved; "standard" emits one status
                question per control in scope.

        Returns:
            AssessmentTemplate describing the questions to ask.
        """
        return await _get_assessment_questions_impl(
            framework=framework,
            function=function,
            category=category,
            control_id=control_id,
        )

    @mcp.tool()
    async def assess_control(
        control_id: str,
        framework: str = "nist-csf-2.0",
        response: str | None = None,
        evaluate_response: bool = False,
    ) -> AssessmentTemplate | AssessmentResult | dict[str, Any]:
        """Assess a control with optional response evaluation.

        This tool provides two modes:
        1. Get assessment questions for a control (evaluate_response=False)
        2. Evaluate a user's response against a control (evaluate_response=True)

        In evaluate_response mode, the tool analyzes the user's response to
        identify maturity level, strengths, gaps, and recommendations.

        Args:
            control_id: Control to assess (e.g., "PR.AC-01")
            framework: Framework ID (default: "nist-csf-2.0")
            response: User's response describing their implementation
                     (required when evaluate_response=True)
            evaluate_response: If True, evaluate the response; if False, return questions

        Returns:
            AssessmentTemplate if evaluate_response=False
            AssessmentResult if evaluate_response=True
            Error dict if control not found
        """
        manager = FrameworkManager()

        if evaluate_response:
            if not response:
                return {"error": "response parameter is required when evaluate_response=True"}

            # Get control details for context
            control_details = await manager.get_control_details(
                framework_id=framework,
                control_id=control_id,
            )

            if not control_details:
                return {
                    "error": f"Control {control_id} not found in framework {framework}",
                    "control_id": control_id,
                    "control_name": "Unknown",
                    "framework_id": framework,
                    "maturity_level": "not_addressed",
                    "strengths": [],
                    "gaps": ["Control not found in framework"],
                    "recommendations": [],
                }

            # Create orchestrator with config and client
            config = IntelligenceConfig()
            client = OllamaClient(config)
            orchestrator = IntelligenceOrchestrator(config, client)

            # Build context with control details
            context = {
                "control_name": control_details.name,
                "framework_id": framework,
            }

            # Run assessment through orchestrator
            orchestrator_result = await orchestrator.assess(
                control_id=control_id,
                response=response,
                context=context,
            )

            # Build response with backward-compatible fields plus metadata
            result_dict: dict[str, Any] = {
                "control_id": orchestrator_result.control_id,
                "control_name": orchestrator_result.control_name,
                "framework_id": orchestrator_result.framework_id,
                "maturity_level": orchestrator_result.maturity_level,
                "strengths": orchestrator_result.strengths,
                "gaps": orchestrator_result.gaps,
                "recommendations": orchestrator_result.recommendations,
                # New metadata fields
                "analysis_mode": orchestrator_result.metadata.analysis_mode,
                "llm_used": orchestrator_result.metadata.llm_used,
                "degrade_reason": orchestrator_result.metadata.degrade_reason,
            }

            # Add optional LLM enrichment fields if present
            if orchestrator_result.llm_rationale:
                result_dict["llm_rationale"] = orchestrator_result.llm_rationale
            if orchestrator_result.llm_context:
                result_dict["llm_context"] = orchestrator_result.llm_context
            if orchestrator_result.metadata.policy_violations:
                result_dict["policy_violations"] = orchestrator_result.metadata.policy_violations
            if orchestrator_result.metadata.latency_ms is not None:
                result_dict["latency_ms"] = orchestrator_result.metadata.latency_ms

            return result_dict

        else:
            # Return assessment questions for the control
            return await _get_assessment_questions_impl(
                framework=framework,
                control_id=control_id,
            )

    @mcp.tool()
    async def interview_control(
        control_id: str,
        mode: str,
        framework: str = "nist-csf-2.0",
        answers: dict[str, str | list[str]] | None = None,
        project_path: str = ".",
    ) -> dict[str, Any]:
        """Guided Q&A to document a control — like a GRC portal questionnaire but conversational.

        This tool provides three modes:
        1. **start**: Begin interview for a control - returns questions and maturity indicators
        2. **submit**: Submit answers - records implementation summary, links evidence, assesses maturity
        3. **skip**: Skip control - records as not applicable

        Args:
            control_id: Control to interview about (e.g., 'PR.DS-01')
            mode: 'start', 'submit', or 'skip'
            framework: Framework ID (default: 'nist-csf-2.0')
            answers: For submit mode: answers keyed by question ID (e.g., {'q1': 'AES-256', 'q2': ['Databases']})
            project_path: Path to project root (default: current directory)

        Returns:
            InterviewStartResponse for start mode
            InterviewSubmitResponse for submit mode
            InterviewSkipResponse for skip mode
        """
        from pathlib import Path

        from compliance_oracle.documentation.state import ComplianceStateManager

        manager = FrameworkManager()
        state_manager = ComplianceStateManager(Path(project_path))

        if mode == "start":
            return await _interview_start(control_id, framework, manager)
        elif mode == "submit":
            if not answers:
                return {"error": "answers parameter is required for submit mode"}
            return await _interview_submit(
                control_id, framework, answers, manager, state_manager
            )
        elif mode == "skip":
            return await _interview_skip(control_id, framework, state_manager)
        else:
            return {"error": f"Invalid mode '{mode}'. Must be 'start', 'submit', or 'skip'"}
