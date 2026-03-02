"""Shared fixtures for compliance-oracle tests."""

from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from compliance_oracle.documentation.state import ComplianceStateManager
from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import (
    Control,
    ControlDetails,
    ControlDocumentation,
    ControlStatus,
    Evidence,
    EvidenceType,
    FrameworkInfo,
    FrameworkStatus,
    SearchResult,
)
from compliance_oracle.rag.search import ControlSearcher

# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_framework_info() -> FrameworkInfo:
    """Sample framework info for testing."""
    return FrameworkInfo(
        id="nist-csf-2.0",
        name="NIST Cybersecurity Framework 2.0",
        version="2.0",
        status=FrameworkStatus.ACTIVE,
        description="A voluntary framework for managing cybersecurity risk",
        source_url="https://www.nist.gov/cyberframework",
        control_count=106,
    )


@pytest.fixture
def sample_control() -> Control:
    """Sample control for testing."""
    return Control(
        id="PR.AC-01",
        name="Identity and Credentials",
        description="Manage user identities and credentials using automated tools.",
        framework_id="nist-csf-2.0",
        function_id="PR",
        function_name="PROTECT",
        category_id="PR.AC",
        category_name="Identity Management and Access Control",
        implementation_examples=[
            "Implement centralized identity management system",
            "Use MFA for privileged access",
        ],
        informative_references=["NIST SP 800-53: IA-1, IA-2"],
        keywords=["identity", "credentials", "access"],
    )


@pytest.fixture
def sample_control_details(sample_control: Control) -> ControlDetails:
    """Sample control details for testing."""
    return ControlDetails(
        id=sample_control.id,
        name=sample_control.name,
        description=sample_control.description,
        framework_id=sample_control.framework_id,
        function_id=sample_control.function_id,
        function_name=sample_control.function_name,
        category_id=sample_control.category_id,
        category_name=sample_control.category_name,
        implementation_examples=sample_control.implementation_examples,
        informative_references=sample_control.informative_references,
        keywords=sample_control.keywords,
        related_controls=["PR.AC-02", "PR.AC-03"],
        mappings={"nist-800-53-r5": ["IA-1", "IA-2"]},
    )


@pytest.fixture
def sample_search_result() -> SearchResult:
    """Sample search result for testing."""
    return SearchResult(
        control_id="PR.AC-01",
        control_name="Identity and Credentials",
        description="Manage user identities and credentials using automated tools.",
        framework_id="nist-csf-2.0",
        relevance_score=0.95,
    )


@pytest.fixture
def sample_control_documentation() -> ControlDocumentation:
    """Sample control documentation for testing."""
    return ControlDocumentation(
        control_id="PR.AC-01",
        framework_id="nist-csf-2.0",
        status=ControlStatus.IMPLEMENTED,
        implementation_summary="Implemented via Okta SSO with MFA",
        owner="Security Team",
        notes="Review quarterly",
        evidence=[],
        last_updated=datetime(2026, 2, 28, 12, 0, 0),
    )


@pytest.fixture
def sample_evidence() -> Evidence:
    """Sample evidence for testing."""
    return Evidence(
        type=EvidenceType.CONFIG,
        path="config/auth.yaml",
        description="MFA configuration file",
        line_range=(10, 25),
    )


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_framework_manager(
    sample_framework_info: FrameworkInfo,
    sample_control: Control,
    sample_control_details: ControlDetails,
) -> MagicMock:
    """Mock FrameworkManager for testing without real framework data."""
    manager = MagicMock(spec=FrameworkManager)
    manager.list_frameworks = AsyncMock(return_value=[sample_framework_info])
    manager.list_controls = AsyncMock(return_value=[sample_control])
    manager.get_control_details = AsyncMock(return_value=sample_control_details)
    return manager


@pytest.fixture
def mock_control_searcher(
    sample_search_result: SearchResult,
    sample_control_details: ControlDetails,
    sample_control: Control,
) -> MagicMock:
    """Mock ControlSearcher for testing without real RAG index."""
    searcher = MagicMock(spec=ControlSearcher)
    searcher.search = AsyncMock(return_value=[sample_search_result])
    searcher.get_context = AsyncMock(
        return_value={
            "control": sample_control_details.model_dump(),
            "hierarchy": {
                "framework_id": "nist-csf-2.0",
                "function": {
                    "id": "PR",
                    "name": "PROTECT",
                },
                "category": {
                    "id": "PR.AC",
                    "name": "Identity Management and Access Control",
                },
            },
            "siblings": [
                {"id": "PR.AC-02", "name": "Physical Access"},
            ],
            "related": [
                {"id": "PR.AC-03", "name": "Remote Access", "score": 0.85},
            ],
        }
    )
    searcher.is_indexed = AsyncMock(return_value=True)
    searcher.get_indexed_count = AsyncMock(return_value=100)
    return searcher


@pytest.fixture
def mock_state_manager(
    sample_control_documentation: ControlDocumentation,
    tmp_path: Path,
) -> MagicMock:
    """Mock ComplianceStateManager for testing without real state files."""
    manager = MagicMock(spec=ComplianceStateManager)
    manager.get_state = AsyncMock()
    manager.document_control = AsyncMock()
    manager.link_evidence = AsyncMock()
    manager.get_control_documentation = AsyncMock(return_value=sample_control_documentation)
    manager.get_summary = AsyncMock()
    manager.export = AsyncMock(return_value="# Compliance Report\n...")
    return manager


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================


@pytest.fixture
def temp_project_path(tmp_path: Path) -> Path:
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir
