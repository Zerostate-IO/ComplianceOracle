"""Pydantic schemas for compliance data structures."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from compliance_oracle.assessment.contracts import IntelligenceMetadata


class FrameworkStatus(StrEnum):
    """Status of a framework in the system."""

    ACTIVE = "active"
    PLANNED = "planned"
    DEPRECATED = "deprecated"


class ControlStatus(StrEnum):
    """Implementation status for a control."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    PLANNED = "planned"
    NOT_APPLICABLE = "not_applicable"
    NOT_ADDRESSED = "not_addressed"


class ControlRelationship(StrEnum):
    """Type of relationship between mapped controls in different frameworks."""

    EQUIVALENT = "equivalent"
    BROADER = "broader"
    NARROWER = "narrower"
    RELATED = "related"


class EvidenceType(StrEnum):
    """Types of evidence that can be linked."""

    CONFIG = "config"
    CODE = "code"
    DOCUMENT = "document"
    URL = "url"
    SCREENSHOT = "screenshot"
    OTHER = "other"


class Severity(StrEnum):
    """Severity levels for findings."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# --- Framework Models ---


class FrameworkInfo(BaseModel):
    """Basic information about a compliance framework."""

    id: str = Field(description="Unique identifier (e.g., 'nist-csf-2.0')")
    name: str = Field(description="Human-readable name")
    version: str = Field(description="Framework version")
    status: FrameworkStatus = Field(default=FrameworkStatus.ACTIVE)
    description: str | None = Field(default=None)
    source_url: str | None = Field(default=None)
    control_count: int = Field(default=0)


class FrameworkFunction(BaseModel):
    """Top-level function in a framework (e.g., PROTECT, DETECT)."""

    id: str = Field(description="Function identifier (e.g., 'PR')")
    name: str = Field(description="Function name (e.g., 'PROTECT')")
    description: str | None = Field(default=None)


class FrameworkCategory(BaseModel):
    """Category within a function (e.g., PR.AC - Access Control)."""

    id: str = Field(description="Category identifier (e.g., 'PR.AC')")
    name: str = Field(description="Category name")
    description: str | None = Field(default=None)
    function_id: str = Field(description="Parent function ID")


class Control(BaseModel):
    """A single control/subcategory in a framework."""

    id: str = Field(description="Control identifier (e.g., 'PR.AC-01')")
    name: str = Field(description="Control name")
    description: str = Field(description="What this control requires")
    framework_id: str = Field(description="Parent framework ID")
    function_id: str = Field(description="Parent function ID")
    function_name: str = Field(description="Parent function name")
    category_id: str = Field(description="Parent category ID")
    category_name: str = Field(description="Parent category name")
    implementation_examples: list[str] = Field(default_factory=list)
    informative_references: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class ControlDetails(Control):
    """Extended control details including related controls."""

    related_controls: list[str] = Field(default_factory=list)
    mappings: dict[str, list[str]] = Field(
        default_factory=dict, description="Cross-framework mappings"
    )


# --- Search Models ---


class SearchResult(BaseModel):
    """A single search result from RAG."""

    control_id: str
    control_name: str
    description: str
    framework_id: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Response from search_controls."""

    query: str
    framework: str | None = Field(default=None)
    results: list[SearchResult]
    total_results: int


# --- Documentation Models ---


class Evidence(BaseModel):
    """Evidence linked to a control."""

    type: EvidenceType
    path: str = Field(description="File path or URL")
    line_range: tuple[int, int] | None = Field(
        default=None, description="Start and end line numbers"
    )
    description: str


class ControlDocumentation(BaseModel):
    """Documentation for a single control."""

    control_id: str
    framework_id: str

    # Direct, explicit assessment status for this control
    status: ControlStatus

    # Optional status derived from crosswalks with other frameworks
    derived_status: ControlStatus | None = Field(default=None)
    derived_sources: list[dict[str, str]] = Field(
        default_factory=list,
        description=(
            "List of mappings that contributed to derived_status, e.g. "
            "[{'framework_id': 'nist-csf-2.0', 'control_id': 'PR.AC-01', 'relationship': 'equivalent'}]"
        ),
    )

    implementation_summary: str | None = Field(default=None)
    evidence: list[Evidence] = Field(default_factory=list)
    owner: str | None = Field(default=None)
    notes: str | None = Field(default=None)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Optional metadata from hybrid intelligence analysis
    intelligence_metadata: IntelligenceMetadata | None = Field(
        default=None,
        description="Optional metadata describing the analysis mode and any degradation events",
    )

class ComplianceState(BaseModel):
    """Full compliance state for a project."""

    version: str = Field(default="1.0")
    project_name: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    controls: dict[str, ControlDocumentation] = Field(
        default_factory=dict, description="Keyed by 'framework_id:control_id'"
    )


class ComplianceSummary(BaseModel):
    """Summary statistics for compliance state."""

    framework_id: str
    total_controls: int
    implemented: int
    partial: int
    planned: int
    not_applicable: int
    not_addressed: int
    completion_percentage: float = Field(ge=0.0, le=100.0)


# --- Gap Analysis Models ---


class AssessmentAnswerType(StrEnum):
    """Type of answer expected for an assessment question."""

    YES_NO = "yes_no"
    CHOICE = "choice"
    FREE_TEXT = "free_text"


class AssessmentAnswerOption(BaseModel):
    """Single answer option for a multiple-choice assessment question."""

    value: str
    label: str
    maps_to_status: ControlStatus | None = Field(
        default=None,
        description="If set, selecting this option should map to the given control status.",
    )


class AssessmentQuestion(BaseModel):
    """Interview-style question used to assess one or more controls."""

    id: str
    framework_id: str
    control_ids: list[str]
    text: str
    answer_type: AssessmentAnswerType
    answer_options: list[AssessmentAnswerOption] = Field(default_factory=list)


class AssessmentTemplate(BaseModel):
    """Collection of assessment questions for a given scope."""

    framework_id: str
    scope: str = Field(
        description="Scope of the assessment: framework, function, category, or control.",
    )
    function_id: str | None = None
    category_id: str | None = None
    control_ids: list[str] = Field(default_factory=list)
    questions: list[AssessmentQuestion] = Field(default_factory=list)


class ControlMapping(BaseModel):
    """Mapping between controls in different frameworks."""

    source_control_id: str
    source_framework_id: str
    target_control_id: str
    target_framework_id: str
    relationship: ControlRelationship = Field(
        default=ControlRelationship.RELATED,
        description="equivalent, broader, narrower, related",
    )


class GapAnalysisResult(BaseModel):
    """Result of framework gap analysis."""

    current_framework: str
    target_framework: str
    already_covered: list[dict[str, Any]]
    partially_covered: list[dict[str, Any]]
    gaps: list[dict[str, Any]]
    summary: dict[str, Any]


# --- Tool Response Models ---


class ListFrameworksResponse(BaseModel):
    """Response from list_frameworks tool."""

    frameworks: list[FrameworkInfo]


class ListControlsResponse(BaseModel):
    """Response from list_controls tool."""

    framework_id: str
    function: str | None = Field(default=None)
    category: str | None = Field(default=None)
    controls: list[Control]
    total_count: int



# --- Evaluation Models ---


class ContentType(StrEnum):
    """Types of content that can be evaluated."""

    DESIGN_DOC = "design_doc"
    CODE = "code"
    ARCHITECTURE = "architecture"


class ComplianceFinding(BaseModel):
    """A single compliance finding from evaluation."""

    control_id: str = Field(description="Control identifier (e.g., 'PR.AC-01')")
    control_name: str = Field(description="Control name")
    function: str = Field(description="Parent function name")
    category: str = Field(description="Category name")
    finding: str = Field(description="Description of the compliance gap")
    rationale: str = Field(description="Why this is a gap based on control requirements")
    severity: Severity = Field(description="Severity level: low, medium, high, critical")


class EvaluationResponse(BaseModel):
    """Response from evaluate_compliance tool."""

    framework: str = Field(description="Framework used for evaluation")
    findings_count: int = Field(description="Total number of findings")
    findings: list[ComplianceFinding] = Field(
        default_factory=list, description="List of compliance findings"
    )
    evaluated_controls: int = Field(description="Number of controls evaluated")
    compliant_areas: list[str] = Field(
        default_factory=list, description="Areas found to be compliant"
    )
    error: str | None = Field(
        default=None, description="Error message if evaluation failed"
    )
    llm_summary: str | None = Field(
        default=None,
        description="LLM-generated summary of findings (when hybrid mode is available)",
    )
    metadata: IntelligenceMetadata | None = Field(
        default=None,
        description="Optional metadata describing the analysis mode and any degradation events",
    )

class AssessmentResult(BaseModel):
    """Result of assessing a control with a user response."""

    control_id: str = Field(description="Control identifier (e.g., 'PR.AC-01')")
    control_name: str = Field(description="Control name")
    framework_id: str = Field(description="Framework identifier")
    maturity_level: str = Field(
        description="Assessed maturity level: basic, intermediate, advanced, or not_addressed"
    )
    strengths: list[str] = Field(
        default_factory=list, description="Areas where implementation is strong"
    )
    gaps: list[str] = Field(
        default_factory=list, description="Identified gaps in implementation"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for improvement (gap-focused, not prescriptive)"
    )
    metadata: IntelligenceMetadata | None = Field(
        default=None,
        description="Optional metadata describing the analysis mode and any degradation events",
    )

# --- Interview Models ---


class InterviewQuestionType(StrEnum):
    """Types of interview questions."""

    TEXT = "text"
    MULTI_SELECT = "multi_select"
    EVIDENCE_LINK = "evidence_link"


class InterviewQuestion(BaseModel):
    """A single interview question for guided Q&A."""

    id: str = Field(description="Question identifier (e.g., 'q1')")
    question: str = Field(description="The question text")
    type: InterviewQuestionType = Field(description="Type of question")
    options: list[str] | None = Field(
        default=None, description="Options for multi_select questions"
    )
    examples: list[str] | None = Field(
        default=None, description="Example answers for text questions"
    )


class MaturityIndicators(BaseModel):
    """Maturity level descriptions for a control."""

    basic: str = Field(description="Basic maturity level description")
    intermediate: str = Field(description="Intermediate maturity level description")
    advanced: str = Field(description="Advanced maturity level description")


class InterviewStartResponse(BaseModel):
    """Response from interview_control in start mode."""

    control_id: str
    control_name: str
    description: str
    questions: list[InterviewQuestion]
    maturity_indicators: MaturityIndicators


class InterviewSubmitResponse(BaseModel):
    """Response from interview_control in submit mode."""

    control_id: str
    status: str = Field(description="Status after submission: 'documented'")
    recorded: dict[str, Any] = Field(description="Recorded implementation details")
    evidence_linked: int = Field(description="Number of evidence items linked")
    assessed_maturity: str = Field(description="Assessed maturity level")
    follow_up_recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for improvement"
    )


class InterviewSkipResponse(BaseModel):
    """Response from interview_control in skip mode."""

    control_id: str
    status: str = Field(description="Status after skip: 'not_applicable'")
    message: str
