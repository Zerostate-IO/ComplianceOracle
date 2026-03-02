"""Compliance evaluation tools for assessing content against frameworks."""

import re
from typing import Any

from fastmcp import FastMCP

from compliance_oracle.assessment import (
    IntelligenceOrchestrator,
    load_intelligence_config,
)
from compliance_oracle.assessment.llm import OllamaClient
from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import (
    ComplianceFinding,
    ContentType,
    EvaluationResponse,
    Severity,
)
from compliance_oracle.rag.search import ControlSearcher

# Keywords/patterns that indicate compliance with specific control areas
COMPLIANCE_INDICATORS: dict[str, list[str]] = {
    "PR.AC": [
        r"multi[- ]factor",
        r"MFA",
        r"single[- ]sign[- ]on",
        r"SSO",
        r"access[- ]control",
        r"role[- ]based",
        r"RBAC",
        r"identity[- ]management",
        r"authentication",
        r"authorization",
        r"least[- ]privilege",
        r"credential",
        r"password[- ]policy",
    ],
    "PR.AT": [
        r"training",
        r"awareness",
        r"security[- ]education",
        r"phishing[- ]simulation",
        r"user[- ]education",
    ],
    "PR.DS": [
        r"encryption[- ]at[- ]rest",
        r"encryption[- ]in[- ]transit",
        r"TLS",
        r"SSL",
        r"data[- ]classification",
        r"data[- ]protection",
        r"AES[- ]\d+",
        r"backup",
        r"recovery[- ]point",
    ],
    "PR.IP": [
        r"change[- ]management",
        r"vulnerability[- ]scan",
        r"patch[- ]management",
        r"configuration[- ]management",
        r"hardening",
        r"baseline",
    ],
    "PR.MA": [
        r"maintenance",
        r"patching",
        r"update",
        r"upgrade",
        r"lifecycle",
    ],
    "PR.PT": [
        r"network[- ]segmentation",
        r"firewall",
        r"IDS",
        r"IPS",
        r"proxy",
        r"DMZ",
    ],
    "DE.CM": [
        r"monitoring",
        r"logging",
        r"SIEM",
        r"alert",
        r"detection",
        r"anomaly",
        r"continuous[- ]monitoring",
    ],
    "DE.DP": [
        r"security[- ]event",
        r"log[- ]analysis",
        r"threat[- ]detection",
        r"event[- ]correlation",
    ],
    "DE.AE": [
        r"anomaly[- ]detection",
        r"threat[- ]intelligence",
        r"indicator[- ]of[- ]compromise",
        r"IOC",
    ],
    "RS.RP": [
        r"incident[- ]response",
        r"IR[- ]plan",
        r"playbook",
        r"response[- ]procedure",
        r"escalation",
    ],
    "RS.AN": [
        r"forensic",
        r"root[- ]cause[- ]analysis",
        r"incident[- ]analysis",
        r"post[- ]mortem",
    ],
    "RS.CO": [
        r"communication[- ]plan",
        r"stakeholder[- ]notification",
        r"customer[- ]notification",
        r"regulatory[- ]reporting",
    ],
    "RC.RP": [
        r"recovery[- ]plan",
        r"business[- ]continuity",
        r"disaster[- ]recovery",
        r"BCP",
        r"DRP",
    ],
    "GV.OC": [
        r"governance",
        r"policy",
        r"risk[- ]management",
        r"compliance[- ]program",
        r"oversight",
    ],
    "GV.RM": [
        r"risk[- ]assessment",
        r"risk[- ]register",
        r"risk[- ]treatment",
        r"risk[- ]acceptance",
    ],
    "GV.MA": [
        r"security[- ]policy",
        r"standards",
        r"procedures",
        r"guidelines",
    ],
}

# Severity mapping based on control categories/functions
SEVERITY_BY_FUNCTION: dict[str, Severity] = {
    "PR": Severity.HIGH,
    "DE": Severity.MEDIUM,
    "RS": Severity.HIGH,
    "RC": Severity.CRITICAL,
    "GV": Severity.MEDIUM,
}

# Higher severity for specific critical categories
CRITICAL_CATEGORIES: set[str] = {
    "PR.AC",  # Access control
    "PR.DS",  # Data security
    "RS.RP",  # Incident response
    "RC.RP",  # Recovery
}


def _determine_severity(control_id: str, relevance_score: float) -> Severity:
    """Determine severity based on control ID and relevance score.

    Args:
        control_id: The control identifier (e.g., 'PR.AC-01')
        relevance_score: The relevance score from search (0.0-1.0)

    Returns:
        Severity level for the finding.
    """
    # Extract function and category from control ID
    parts = control_id.split(".")
    if len(parts) < 2:
        return Severity.MEDIUM

    function = parts[0]
    category = f"{parts[0]}.{parts[1].split('-')[0]}" if "-" in parts[1] else control_id

    # Critical categories always get high/critical severity
    if category in CRITICAL_CATEGORIES:
        return Severity.CRITICAL if relevance_score > 0.8 else Severity.HIGH

    # Use function-based severity
    base_severity = SEVERITY_BY_FUNCTION.get(function, Severity.MEDIUM)

    # Adjust based on relevance score
    if relevance_score > 0.9 and base_severity == Severity.MEDIUM:
        return Severity.HIGH
    if relevance_score < 0.5 and base_severity == Severity.HIGH:
        return Severity.MEDIUM

    return base_severity
    return base_severity


def _find_compliant_areas(content: str, content_lower: str) -> list[str]:
    """Identify areas of content that indicate compliance.

    Args:
        content: Original content
        content_lower: Lowercase version for matching

    Returns:
        List of compliant area descriptions.
    """
    compliant_areas: list[str] = []

    for category, patterns in COMPLIANCE_INDICATORS.items():
        for pattern in patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                # Found a compliance indicator
                compliant_areas.append(f"Addresses {category} requirements ({pattern})")
                break  # Only count each category once

    return compliant_areas


def _generate_finding(
    control_id: str,
    control_name: str,
    function: str,
    category: str,
    control_description: str,
    content_type: ContentType,
    relevance_score: float,
) -> ComplianceFinding:
    """Generate a compliance finding for a control gap.

    The finding describes the gap without suggesting fixes.

    Args:
        control_id: Control identifier
        control_name: Control name
        function: Parent function name
        category: Category name
        control_description: What the control requires
        content_type: Type of content being evaluated
        relevance_score: Search relevance score

    Returns:
        A ComplianceFinding object.
    """
    severity = _determine_severity(control_id, relevance_score)

    # Generate finding text based on content type
    content_type_labels = {
        ContentType.DESIGN_DOC: "design document",
        ContentType.CODE: "code",
        ContentType.ARCHITECTURE: "architecture",
    }
    content_label = content_type_labels.get(content_type, "content")

    finding = f"No evidence found in {content_label} addressing {control_name}"
    rationale = (
        f"CSF {control_id} requires: {control_description}. "
        f"The evaluated {content_label} does not demonstrate coverage of this requirement."
    )

    return ComplianceFinding(
        control_id=control_id,
        control_name=control_name,
        function=function,
        category=category,
        finding=finding,
        rationale=rationale,
        severity=severity,
    )


async def _evaluate_against_controls(
    content: str,
    content_type: ContentType,
    framework: str,
    focus_areas: list[str] | None,
    searcher: ControlSearcher,
    manager: FrameworkManager,
) -> tuple[list[ComplianceFinding], int, list[str]]:
    """Evaluate content against framework controls.

    Args:
        content: Content to evaluate
        content_type: Type of content
        framework: Framework ID
        focus_areas: Optional focus areas (functions/categories)
        searcher: ControlSearcher instance
        manager: FrameworkManager instance

    Returns:
        Tuple of (findings, evaluated_controls_count, compliant_areas)
    """
    content_lower = content.lower()
    findings: list[ComplianceFinding] = []
    evaluated_controls: set[str] = set()

    # Find compliant areas first
    compliant_areas = _find_compliant_areas(content, content_lower)

    # Determine search scope based on focus areas
    search_queries: list[tuple[str, str | None]] = []

    if focus_areas:
        for area in focus_areas:
            # Treat focus area as a search query
            search_queries.append((f"security controls for {area}", area))
    else:
        # General security evaluation queries
        search_queries = [
            ("access control authentication identity management", None),
            ("data protection encryption security", None),
            ("monitoring logging detection", None),
            ("incident response recovery", None),
            ("governance policy risk management", None),
        ]

    # Search for relevant controls
    seen_controls: set[str] = set()

    for query, _area in search_queries:
        results = await searcher.search(
            query=query,
            framework_id=framework,
            limit=15,
        )

        for result in results:
            if result.control_id in seen_controls:
                continue
            seen_controls.add(result.control_id)
            evaluated_controls.add(result.control_id)

            # Check if content addresses this control
            control_details = await manager.get_control_details(
                framework_id=framework,
                control_id=result.control_id,
            )

            if not control_details:
                continue

            # Check if any compliance indicators for this category are present
            category_prefix = ".".join(result.control_id.split(".")[:2])
            if "-" in category_prefix:
                category_prefix = category_prefix.split("-")[0]

            patterns = COMPLIANCE_INDICATORS.get(category_prefix, [])
            has_indicator = any(re.search(p, content_lower, re.IGNORECASE) for p in patterns)

            # High relevance + no indicator = potential gap
            if result.relevance_score > 0.6 and not has_indicator:
                finding = _generate_finding(
                    control_id=result.control_id,
                    control_name=result.control_name,
                    function=control_details.function_name,
                    category=control_details.category_name,
                    control_description=control_details.description,
                    content_type=content_type,
                    relevance_score=result.relevance_score,
                )
                findings.append(finding)

    return findings, len(evaluated_controls), compliant_areas



async def evaluate_compliance(
    content: str,
    content_type: str = "design_doc",
    framework: str = "nist-csf-2.0",
    focus_areas: list[str] | None = None,
    manager: FrameworkManager | None = None,
    searcher: ControlSearcher | None = None,
) -> dict[str, Any]:
    """Evaluate content for compliance against a framework.

    This tool identifies compliance gaps without suggesting fixes.
    It uses semantic search to find relevant controls and analyzes
    the content for evidence of compliance.

    Args:
        content: Design document text, code, or architecture to evaluate
        content_type: Type of content ('design_doc', 'code', 'architecture')
        framework: Framework to evaluate against (default: 'nist-csf-2.0')
        focus_areas: Optional list of functions/categories to focus on
                    (e.g., ['PR', 'DE', 'PR.AC'])
        manager: Optional FrameworkManager instance (for testing)
        searcher: Optional ControlSearcher instance (for testing)

    Returns:
        Evaluation results including findings and compliant areas.

    Example:
        evaluate_compliance(
            content="Our system uses MFA and encrypts data at rest...",
            content_type="design_doc",
            framework="nist-csf-2.0",
            focus_areas=["PR"]
        )
    """
    # Validate content_type
    try:
        ct = ContentType(content_type)
    except ValueError:
        ct = ContentType.DESIGN_DOC

    # Initialize components if not provided
    if manager is None:
        manager = FrameworkManager()
    if searcher is None:
        searcher = ControlSearcher(framework_manager=manager)

    # Check if framework is indexed
    is_indexed = await searcher.is_indexed(framework)
    if not is_indexed:
        # Try to index on-the-fly
        indexed_count = await searcher.index_framework(framework)
        if indexed_count == 0:
            return EvaluationResponse(
                framework=framework,
                findings_count=0,
                findings=[],
                evaluated_controls=0,
                compliant_areas=[],
                error=f"Framework '{framework}' not found or has no controls",
            ).model_dump()

    # Perform deterministic evaluation FIRST (source of truth)
    findings, evaluated_count, compliant_areas = await _evaluate_against_controls(
        content=content,
        content_type=ct,
        framework=framework,
        focus_areas=focus_areas,
        searcher=searcher,
        manager=manager,
    )

    # Initialize orchestrator for optional LLM enrichment
    config = load_intelligence_config()

    # Create OllamaClient only if hybrid mode is enabled
    ollama_client: OllamaClient | None = None
    if config.intelligence_mode == "hybrid":
        try:
            ollama_client = OllamaClient(config)
        except Exception:
            # Client creation failed, will degrade to deterministic
            ollama_client = None

    orchestrator = IntelligenceOrchestrator(config, ollama_client)

    # Prepare controls for orchestrator evaluation
    # Convert our findings to control format for orchestrator
    evaluated_controls = [
        {
            "id": finding.control_id,
            "name": finding.control_name,
            "function_name": finding.function,
            "category_name": finding.category,
        }
        for finding in findings
    ]

    # Use orchestrator to get LLM summary and metadata
    # Deterministic findings remain the source of truth
    orchestrator_result = await orchestrator.evaluate(
        content=content,
        content_type=content_type,
        controls=evaluated_controls,
    )

    # Build response using deterministic findings + orchestrator enrichment
    response = EvaluationResponse(
        framework=framework,
        findings_count=len(findings),
        findings=findings,  # Deterministic findings preserved
        evaluated_controls=evaluated_count,
        compliant_areas=compliant_areas,
        llm_summary=orchestrator_result.llm_summary,
        metadata=orchestrator_result.metadata,
    )

    return response.model_dump()


def register_evaluation_tools(mcp: FastMCP) -> None:
    """Register evaluation tools with the MCP server."""

    @mcp.tool()
    async def _evaluate_compliance(
        content: str,
        content_type: str = "design_doc",
        framework: str = "nist-csf-2.0",
        focus_areas: list[str] | None = None,
    ) -> dict[str, Any]:
        """Evaluate content for compliance against a framework.

        This tool identifies compliance gaps without suggesting fixes.
        It uses semantic search to find relevant controls and analyzes
        the content for evidence of compliance.

        Args:
            content: Design document text, code, or architecture to evaluate
            content_type: Type of content ('design_doc', 'code', 'architecture')
            framework: Framework to evaluate against (default: 'nist-csf-2.0')
            focus_areas: Optional list of functions/categories to focus on
                        (e.g., ['PR', 'DE', 'PR.AC'])

        Returns:
            Evaluation results including findings and compliant areas.
        """
        return await evaluate_compliance(
            content=content,
            content_type=content_type,
            framework=framework,
            focus_areas=focus_areas,
        )
