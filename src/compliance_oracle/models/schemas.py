"""Pydantic schemas for compliance data structures."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FrameworkStatus(str, Enum):
    """Status of a framework in the system."""

    ACTIVE = "active"
    PLANNED = "planned"
    DEPRECATED = "deprecated"


class ControlStatus(str, Enum):
    """Implementation status for a control."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    PLANNED = "planned"
    NOT_APPLICABLE = "not_applicable"
    NOT_ADDRESSED = "not_addressed"


class ControlRelationship(str, Enum):
    """Type of relationship between mapped controls in different frameworks."""

    EQUIVALENT = "equivalent"
    BROADER = "broader"
    NARROWER = "narrower"
    RELATED = "related"


class EvidenceType(str, Enum):
    """Types of evidence that can be linked."""

    CONFIG = "config"
    CODE = "code"
    DOCUMENT = "document"
    URL = "url"
    SCREENSHOT = "screenshot"
    OTHER = "other"


class Severity(str, Enum):
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
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ComplianceState(BaseModel):
    """Full compliance state for a project."""

    version: str = Field(default="1.0")
    project_name: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
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


class AssessmentAnswerType(str, Enum):
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
