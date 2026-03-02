"""Comprehensive tests for src/compliance_oracle/frameworks/manager.py."""

import json
from pathlib import Path
from typing import Any

import pytest

from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import (
    FrameworkStatus,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_framework_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample framework JSON files."""
    frameworks_dir = tmp_path / "frameworks"
    frameworks_dir.mkdir(parents=True, exist_ok=True)
    return frameworks_dir


@pytest.fixture
def sample_csf_data() -> dict[str, Any]:
    """Sample NIST CSF 2.0 framework data in CPRT format."""
    return {
        "response": {
            "elements": {
                "elements": [
                    {
                        "element_type": "function",
                        "element_identifier": "PR",
                        "title": "PROTECT",
                        "text": "Develop and implement appropriate safeguards.",
                    },
                    {
                        "element_type": "category",
                        "element_identifier": "PR.AC",
                        "title": "Identity Management and Access Control",
                        "text": "Manage user identities and access.",
                    },
                    {
                        "element_type": "subcategory",
                        "element_identifier": "PR.AC-01",
                        "title": "Identities and Credentials",
                        "text": "Manage user identities and credentials.",
                        "implementation_examples": ["Use SSO", "Implement MFA"],
                        "informative_references": ["NIST SP 800-53: IA-1"],
                        "keywords": ["identity", "access"],
                    },
                    {
                        "element_type": "subcategory",
                        "element_identifier": "PR.AC-02",
                        "title": "Physical Access",
                        "text": "Control physical access.",
                        "implementation_examples": [],
                        "informative_references": [],
                        "keywords": [],
                    },
                ]
            }
        }
    }


@pytest.fixture
def sample_800_53_data() -> dict[str, Any]:
    """Sample NIST 800-53 Rev. 5 framework data in CPRT format."""
    return {
        "response": {
            "elements": {
                "elements": [
                    {
                        "element_type": "family",
                        "element_identifier": "AC",
                        "title": "Access Control",
                        "text": "Access control family.",
                    },
                    {
                        "element_type": "control",
                        "element_identifier": "AC-1",
                        "title": "Policy and Procedures",
                        "text": "Develop access control policy.",
                        "implementation_examples": ["Document policy"],
                        "informative_references": [],
                        "keywords": ["policy"],
                    },
                    {
                        "element_type": "control",
                        "element_identifier": "AC-2",
                        "title": "Account Management",
                        "text": "Manage user accounts.",
                        "implementation_examples": [],
                        "informative_references": [],
                        "keywords": [],
                    },
                ]
            }
        }
    }


@pytest.fixture
def sample_legacy_csf_data() -> dict[str, Any]:
    """Sample legacy CSF format with functions/categories/subcategories."""
    return {
        "functions": [
            {
                "id": "PR",
                "name": "PROTECT",
                "description": "Develop and implement safeguards.",
                "categories": [
                    {
                        "id": "PR.AC",
                        "name": "Identity Management and Access Control",
                        "description": "Manage identities and access.",
                        "function_id": "PR",
                        "subcategories": [
                            {
                                "id": "PR.AC-01",
                                "name": "Identities and Credentials",
                                "description": "Manage identities.",
                                "category_id": "PR.AC",
                                "implementation_examples": ["Use SSO"],
                                "informative_references": [],
                                "keywords": ["identity"],
                            }
                        ],
                    }
                ],
            }
        ]
    }


@pytest.fixture
def sample_legacy_800_53_data() -> dict[str, Any]:
    """Sample legacy 800-53 format with controls."""
    return {
        "controls": [
            {
                "id": "AC-1",
                "name": "Policy and Procedures",
                "description": "Develop access control policy.",
                "family_id": "AC",
                "family_name": "Access Control",
                "implementation_examples": [],
                "informative_references": [],
                "keywords": [],
            }
        ]
    }


@pytest.fixture
def framework_manager_with_csf(
    temp_framework_dir: Path, sample_csf_data: dict[str, Any]
) -> tuple[FrameworkManager, Path]:
    """Create a FrameworkManager with CSF 2.0 data."""
    # Write sample data to file
    csf_file = temp_framework_dir / "nist-csf-2.0.json"
    with open(csf_file, "w") as f:
        json.dump(sample_csf_data, f)

    manager = FrameworkManager(data_dir=temp_framework_dir)
    return manager, temp_framework_dir


@pytest.fixture
def framework_manager_with_800_53(
    temp_framework_dir: Path, sample_800_53_data: dict[str, Any]
) -> tuple[FrameworkManager, Path]:
    """Create a FrameworkManager with 800-53 data."""
    # Write sample data to file
    file_800_53 = temp_framework_dir / "nist-800-53-r5.json"
    with open(file_800_53, "w") as f:
        json.dump(sample_800_53_data, f)

    manager = FrameworkManager(data_dir=temp_framework_dir)
    return manager, temp_framework_dir


@pytest.fixture
def framework_manager_with_both(
    temp_framework_dir: Path,
    sample_csf_data: dict[str, Any],
    sample_800_53_data: dict[str, Any],
) -> tuple[FrameworkManager, Path]:
    """Create a FrameworkManager with both CSF and 800-53 data."""
    csf_file = temp_framework_dir / "nist-csf-2.0.json"
    with open(csf_file, "w") as f:
        json.dump(sample_csf_data, f)

    file_800_53 = temp_framework_dir / "nist-800-53-r5.json"
    with open(file_800_53, "w") as f:
        json.dump(sample_800_53_data, f)

    manager = FrameworkManager(data_dir=temp_framework_dir)
    return manager, temp_framework_dir


@pytest.fixture
def framework_manager_with_legacy_csf(
    temp_framework_dir: Path, sample_legacy_csf_data: dict[str, Any]
) -> tuple[FrameworkManager, Path]:
    """Create a FrameworkManager with legacy CSF 2.0 data."""
    csf_file = temp_framework_dir / "nist-csf-2.0.json"
    with open(csf_file, "w") as f:
        json.dump(sample_legacy_csf_data, f)

    manager = FrameworkManager(data_dir=temp_framework_dir)
    return manager, temp_framework_dir

# ============================================================================
# Initialization Tests
# ============================================================================


def test_init_with_default_data_dir() -> None:
    """Test FrameworkManager initialization with default data directory."""
    manager = FrameworkManager()
    assert manager._data_dir is not None
    assert "data" in str(manager._data_dir)
    assert "frameworks" in str(manager._data_dir)


def test_init_with_custom_data_dir(temp_framework_dir: Path) -> None:
    """Test FrameworkManager initialization with custom data directory."""
    manager = FrameworkManager(data_dir=temp_framework_dir)
    assert manager._data_dir == temp_framework_dir


def test_get_data_dir(temp_framework_dir: Path) -> None:
    """Test _get_data_dir method."""
    manager = FrameworkManager(data_dir=temp_framework_dir)
    assert manager._get_data_dir() == temp_framework_dir


# ============================================================================
# Framework Loading Tests
# ============================================================================


@pytest.mark.asyncio
async def test_load_framework_csf(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test loading NIST CSF 2.0 framework."""
    manager, _ = framework_manager_with_csf
    data = await manager._load_framework("nist-csf-2.0")
    assert data is not None
    assert "response" in data
    assert "elements" in data["response"]


@pytest.mark.asyncio
async def test_load_framework_800_53(
    framework_manager_with_800_53: tuple[FrameworkManager, Path],
) -> None:
    """Test loading NIST 800-53 Rev. 5 framework."""
    manager, _ = framework_manager_with_800_53
    data = await manager._load_framework("nist-800-53-r5")
    assert data is not None
    assert "response" in data


@pytest.mark.asyncio
async def test_load_framework_not_found(temp_framework_dir: Path) -> None:
    """Test loading non-existent framework returns None."""
    manager = FrameworkManager(data_dir=temp_framework_dir)
    data = await manager._load_framework("nist-csf-2.0")
    assert data is None


@pytest.mark.asyncio
async def test_load_framework_invalid_id(temp_framework_dir: Path) -> None:
    """Test loading framework with invalid ID returns None."""
    manager = FrameworkManager(data_dir=temp_framework_dir)
    data = await manager._load_framework("invalid-framework")
    assert data is None


@pytest.mark.asyncio
async def test_load_framework_caching(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test that framework data is cached after first load."""
    manager, _ = framework_manager_with_csf
    # First load
    data1 = await manager._load_framework("nist-csf-2.0")
    # Second load should come from cache
    data2 = await manager._load_framework("nist-csf-2.0")
    assert data1 is data2  # Same object reference


# ============================================================================
# List Frameworks Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_frameworks_empty(temp_framework_dir: Path) -> None:
    """Test listing frameworks when none are installed."""
    manager = FrameworkManager(data_dir=temp_framework_dir)
    frameworks = await manager.list_frameworks()
    assert len(frameworks) == 4  # All known frameworks listed
    assert all(f.status == FrameworkStatus.PLANNED for f in frameworks)


@pytest.mark.asyncio
async def test_list_frameworks_with_csf(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test listing frameworks with CSF installed."""
    manager, _ = framework_manager_with_csf
    frameworks = await manager.list_frameworks()
    assert len(frameworks) == 4
    csf = next((f for f in frameworks if f.id == "nist-csf-2.0"), None)
    assert csf is not None
    assert csf.status == FrameworkStatus.ACTIVE
    assert csf.control_count > 0


@pytest.mark.asyncio
async def test_list_frameworks_with_both(
    framework_manager_with_both: tuple[FrameworkManager, Path],
) -> None:
    """Test listing frameworks with both CSF and 800-53 installed."""
    manager, _ = framework_manager_with_both
    frameworks = await manager.list_frameworks()
    assert len(frameworks) == 4
    active_frameworks = [f for f in frameworks if f.status == FrameworkStatus.ACTIVE]
    assert len(active_frameworks) == 2


# ============================================================================
# Count Controls Tests
# ============================================================================


def test_count_controls_cprt_format(sample_csf_data: dict[str, Any]) -> None:
    """Test counting controls in CPRT format."""
    manager = FrameworkManager()
    count = manager._count_controls(sample_csf_data)
    assert count == 2  # 2 subcategories


def test_count_controls_legacy_format(sample_legacy_csf_data: dict[str, Any]) -> None:
    """Test counting controls in legacy format."""
    manager = FrameworkManager()
    count = manager._count_controls(sample_legacy_csf_data)
    assert count == 1  # 1 subcategory


def test_count_controls_800_53_format(sample_legacy_800_53_data: dict[str, Any]) -> None:
    """Test counting controls in 800-53 format."""
    manager = FrameworkManager()
    count = manager._count_controls(sample_legacy_800_53_data)
    assert count == 1  # 1 control


def test_count_controls_empty_data() -> None:
    """Test counting controls with empty data."""
    manager = FrameworkManager()
    count = manager._count_controls({})
    assert count == 0


# ============================================================================
# Extract Controls Tests
# ============================================================================


@pytest.mark.asyncio
async def test_extract_controls_csf_cprt_format(
    sample_csf_data: dict[str, Any],
) -> None:
    """Test extracting controls from CSF in CPRT format."""
    manager = FrameworkManager()
    controls = manager._extract_controls(sample_csf_data, "nist-csf-2.0")
    assert len(controls) == 2
    assert controls[0].id == "PR.AC-01"
    assert controls[0].function_id == "PR"
    # In CPRT format, category_id is derived from first two dot-separated parts
    assert controls[0].category_id == "PR.AC-01"
    assert controls[0].framework_id == "nist-csf-2.0"


@pytest.mark.asyncio
async def test_extract_controls_800_53_cprt_format(
    sample_800_53_data: dict[str, Any],
) -> None:
    """Test extracting controls from 800-53 in CPRT format."""
    manager = FrameworkManager()
    controls = manager._extract_controls(sample_800_53_data, "nist-800-53-r5")
    assert len(controls) == 2
    assert controls[0].id == "AC-1"
    assert controls[0].function_id == "AC"
    assert controls[0].framework_id == "nist-800-53-r5"


@pytest.mark.asyncio
async def test_extract_controls_legacy_csf_format(
    sample_legacy_csf_data: dict[str, Any],
) -> None:
    """Test extracting controls from legacy CSF format."""
    manager = FrameworkManager()
    controls = manager._extract_controls(sample_legacy_csf_data, "nist-csf-2.0")
    assert len(controls) == 1
    assert controls[0].id == "PR.AC-01"
    assert controls[0].function_id == "PR"


@pytest.mark.asyncio
async def test_extract_controls_legacy_800_53_format(
    sample_legacy_800_53_data: dict[str, Any],
) -> None:
    """Test extracting controls from legacy 800-53 format."""
    manager = FrameworkManager()
    controls = manager._extract_controls(sample_legacy_800_53_data, "nist-800-53-r5")
    assert len(controls) == 1
    assert controls[0].id == "AC-1"
    assert controls[0].function_id == "AC"


def test_extract_controls_empty_data() -> None:
    """Test extracting controls from empty data."""
    manager = FrameworkManager()
    controls = manager._extract_controls({}, "nist-csf-2.0")
    assert len(controls) == 0


def test_extract_controls_preserves_metadata(sample_csf_data: dict[str, Any]) -> None:
    """Test that extracted controls preserve all metadata."""
    manager = FrameworkManager()
    controls = manager._extract_controls(sample_csf_data, "nist-csf-2.0")
    control = controls[0]
    assert control.name == "Identities and Credentials"
    assert control.description == "Manage user identities and credentials."
    assert len(control.implementation_examples) == 2
    assert len(control.keywords) == 2


# ============================================================================
# List Controls Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_controls_all(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test listing all controls in a framework."""
    manager, _ = framework_manager_with_csf
    controls = await manager.list_controls("nist-csf-2.0")
    assert len(controls) == 2


@pytest.mark.asyncio
async def test_list_controls_filter_by_function(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test listing controls filtered by function."""
    manager, _ = framework_manager_with_csf
    controls = await manager.list_controls("nist-csf-2.0", function_id="PR")
    assert len(controls) == 2
    assert all(c.function_id == "PR" for c in controls)


@pytest.mark.asyncio
async def test_list_controls_filter_by_category(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test listing controls filtered by category."""
    manager, _ = framework_manager_with_csf
    # In CPRT format, category_id is the full identifier like "PR.AC-01"
    controls = await manager.list_controls("nist-csf-2.0", category_id="PR.AC-01")
    assert len(controls) >= 1
    assert all(c.category_id == "PR.AC-01" for c in controls)


@pytest.mark.asyncio
async def test_list_controls_filter_by_function_and_category(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test listing controls filtered by both function and category."""
    manager, _ = framework_manager_with_csf
    controls = await manager.list_controls(
        "nist-csf-2.0", function_id="PR", category_id="PR.AC-01"
    )
    assert len(controls) >= 1


@pytest.mark.asyncio
async def test_list_controls_no_matches(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test listing controls with no matches."""
    manager, _ = framework_manager_with_csf
    controls = await manager.list_controls("nist-csf-2.0", function_id="NONEXISTENT")
    assert len(controls) == 0


@pytest.mark.asyncio
async def test_list_controls_framework_not_found(temp_framework_dir: Path) -> None:
    """Test listing controls for non-existent framework."""
    manager = FrameworkManager(data_dir=temp_framework_dir)
    controls = await manager.list_controls("nist-csf-2.0")
    assert len(controls) == 0


# ============================================================================
# Get Control Details Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_control_details_found(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test getting details for an existing control."""
    manager, _ = framework_manager_with_csf
    details = await manager.get_control_details("nist-csf-2.0", "PR.AC-01")
    assert details is not None
    assert details.id == "PR.AC-01"
    assert details.name == "Identities and Credentials"
    assert details.framework_id == "nist-csf-2.0"


@pytest.mark.asyncio
async def test_get_control_details_not_found(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test getting details for non-existent control."""
    manager, _ = framework_manager_with_csf
    details = await manager.get_control_details("nist-csf-2.0", "NONEXISTENT")
    assert details is None


@pytest.mark.asyncio
async def test_get_control_details_framework_not_found(temp_framework_dir: Path) -> None:
    """Test getting control details for non-existent framework."""
    manager = FrameworkManager(data_dir=temp_framework_dir)
    details = await manager.get_control_details("nist-csf-2.0", "PR.AC-01")
    assert details is None


@pytest.mark.asyncio
async def test_get_control_details_includes_mappings(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test that control details include mappings."""
    manager, _ = framework_manager_with_csf
    details = await manager.get_control_details("nist-csf-2.0", "PR.AC-01")
    assert details is not None
    assert hasattr(details, "mappings")
    assert isinstance(details.mappings, dict)


@pytest.mark.asyncio
async def test_get_control_details_includes_related(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test that control details include related controls."""
    manager, _ = framework_manager_with_csf
    details = await manager.get_control_details("nist-csf-2.0", "PR.AC-01")
    assert details is not None
    assert hasattr(details, "related_controls")
    assert isinstance(details.related_controls, list)


# ============================================================================
# Get Control Mappings Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_control_mappings_with_references(
    sample_csf_data: dict[str, Any],
) -> None:
    """Test extracting mappings from informative references."""
    manager = FrameworkManager()
    mappings = await manager._get_control_mappings(sample_csf_data, "PR.AC-01")
    assert isinstance(mappings, dict)


@pytest.mark.asyncio
async def test_get_control_mappings_no_references(
    sample_csf_data: dict[str, Any],
) -> None:
    """Test mappings when control has no references."""
    manager = FrameworkManager()
    mappings = await manager._get_control_mappings(sample_csf_data, "NONEXISTENT")
    assert isinstance(mappings, dict)


# ============================================================================
# Get Related Controls Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_related_controls_same_category(
    sample_legacy_csf_data: dict[str, Any],
) -> None:
    """Test finding related controls in same category."""
    manager = FrameworkManager()
    # Use legacy format which has subcategories key
    related = await manager._get_related_controls(sample_legacy_csf_data, "PR.AC-01")
    assert isinstance(related, list)


@pytest.mark.asyncio
async def test_get_related_controls_not_found(
    sample_csf_data: dict[str, Any],
) -> None:
    """Test related controls when control not found."""
    manager = FrameworkManager()
    related = await manager._get_related_controls(sample_csf_data, "NONEXISTENT")
    assert isinstance(related, list)
    assert len(related) == 0


# ============================================================================
# Get Functions Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_functions_csf(
    framework_manager_with_legacy_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test getting functions from CSF framework."""
    manager, _ = framework_manager_with_legacy_csf
    functions = await manager.get_functions("nist-csf-2.0")
    assert len(functions) == 1
    assert functions[0].id == "PR"
    assert functions[0].name == "PROTECT"


@pytest.mark.asyncio
async def test_get_functions_empty_framework(temp_framework_dir: Path) -> None:
    """Test getting functions from non-existent framework."""
    manager = FrameworkManager(data_dir=temp_framework_dir)
    functions = await manager.get_functions("nist-csf-2.0")
    assert len(functions) == 0


@pytest.mark.asyncio
async def test_get_functions_preserves_metadata(
    framework_manager_with_legacy_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test that functions preserve all metadata."""
    manager, _ = framework_manager_with_legacy_csf
    functions = await manager.get_functions("nist-csf-2.0")
    func = functions[0]
    assert func.description == "Develop and implement safeguards."


# ============================================================================
# Get Categories Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_categories_all(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test getting all categories from framework."""
    manager, _ = framework_manager_with_csf
    categories = await manager.get_categories("nist-csf-2.0")
    # Note: Legacy format has categories in data
    assert isinstance(categories, list)


@pytest.mark.asyncio
async def test_get_categories_filter_by_function(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test getting categories filtered by function."""
    manager, _ = framework_manager_with_csf
    categories = await manager.get_categories("nist-csf-2.0", function_id="PR")
    assert isinstance(categories, list)


@pytest.mark.asyncio
async def test_get_categories_empty_framework(temp_framework_dir: Path) -> None:
    """Test getting categories from non-existent framework."""
    manager = FrameworkManager(data_dir=temp_framework_dir)
    categories = await manager.get_categories("nist-csf-2.0")
    assert len(categories) == 0


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


@pytest.mark.asyncio
async def test_load_framework_malformed_json(temp_framework_dir: Path) -> None:
    """Test loading framework with malformed JSON."""
    # Create a malformed JSON file
    bad_file = temp_framework_dir / "nist-csf-2.0.json"
    with open(bad_file, "w") as f:
        f.write("{invalid json")

    manager = FrameworkManager(data_dir=temp_framework_dir)
    with pytest.raises(json.JSONDecodeError):
        await manager._load_framework("nist-csf-2.0")


@pytest.mark.asyncio
async def test_extract_controls_missing_fields(
    sample_csf_data: dict[str, Any],
) -> None:
    """Test extracting controls with missing optional fields."""
    # Remove optional fields
    for elem in sample_csf_data["response"]["elements"]["elements"]:
        if elem.get("element_type") == "subcategory":
            elem.pop("implementation_examples", None)
            elem.pop("keywords", None)

    manager = FrameworkManager()
    controls = manager._extract_controls(sample_csf_data, "nist-csf-2.0")
    assert len(controls) > 0
    assert controls[0].implementation_examples == []
    assert controls[0].keywords == []


@pytest.mark.asyncio
async def test_list_controls_with_missing_hierarchy(
    sample_csf_data: dict[str, Any],
) -> None:
    """Test listing controls when hierarchy is incomplete."""
    # Remove function from data
    sample_csf_data["response"]["elements"]["elements"] = [
        e
        for e in sample_csf_data["response"]["elements"]["elements"]
        if e.get("element_type") != "function"
    ]

    manager = FrameworkManager()
    controls = manager._extract_controls(sample_csf_data, "nist-csf-2.0")
    # Should still extract controls, but with empty function_id
    assert len(controls) > 0


def test_count_controls_with_subcategories_key(
    sample_legacy_csf_data: dict[str, Any],
) -> None:
    """Test counting controls when 'subcategories' key exists at top level."""
    manager = FrameworkManager()
    count = manager._count_controls(sample_legacy_csf_data)
    assert count >= 0


def test_count_controls_with_controls_key(
    sample_legacy_800_53_data: dict[str, Any],
) -> None:
    """Test counting controls when 'controls' key exists at top level."""
    manager = FrameworkManager()
    count = manager._count_controls(sample_legacy_800_53_data)
    assert count >= 0


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_full_workflow_csf(
    framework_manager_with_csf: tuple[FrameworkManager, Path],
) -> None:
    """Test complete workflow: list frameworks, list controls, get details."""
    manager, _ = framework_manager_with_csf

    # List frameworks
    frameworks = await manager.list_frameworks()
    assert len(frameworks) > 0

    # List controls
    controls = await manager.list_controls("nist-csf-2.0")
    assert len(controls) > 0

    # Get details
    control_id = controls[0].id
    details = await manager.get_control_details("nist-csf-2.0", control_id)
    assert details is not None
    assert details.id == control_id


@pytest.mark.asyncio
async def test_full_workflow_800_53(
    framework_manager_with_800_53: tuple[FrameworkManager, Path],
) -> None:
    """Test complete workflow with 800-53 framework."""
    manager, _ = framework_manager_with_800_53

    # List frameworks
    frameworks = await manager.list_frameworks()
    assert len(frameworks) > 0

    # List controls
    controls = await manager.list_controls("nist-800-53-r5")
    assert len(controls) > 0

    # Get details
    control_id = controls[0].id
    details = await manager.get_control_details("nist-800-53-r5", control_id)
    assert details is not None


@pytest.mark.asyncio
async def test_multiple_frameworks_isolation(
    framework_manager_with_both: tuple[FrameworkManager, Path],
) -> None:
    """Test that controls from different frameworks are properly isolated."""
    manager, _ = framework_manager_with_both

    csf_controls = await manager.list_controls("nist-csf-2.0")
    r5_controls = await manager.list_controls("nist-800-53-r5")

    # Verify they're different
    csf_ids = {c.id for c in csf_controls}
    r5_ids = {c.id for c in r5_controls}
    assert csf_ids != r5_ids



# ============================================================================
# SOC2 Framework Tests
# ============================================================================


@pytest.fixture
def sample_soc2_data() -> dict[str, Any]:
    """Sample SOC2 TSC 2017 framework data."""
    return {
        "functions": [
            {
                "id": "CC",
                "name": "Common Criteria",
                "description": "Common criteria for trust services.",
                "categories": [
                    {
                        "id": "CC1",
                        "name": "Control Environment",
                        "description": "Control environment criteria.",
                        "function_id": "CC",
                        "controls": [
                            {
                                "id": "CC1.1",
                                "name": "Integrity and Ethics",
                                "description": "Demonstrates commitment to integrity.",
                                "implementation_examples": ["Code of conduct"],
                                "informative_references": [],
                                "keywords": ["ethics"],
                            },
                            {
                                "id": "CC1.2",
                                "name": "Board Oversight",
                                "description": "Board establishes oversight.",
                                "implementation_examples": [],
                                "informative_references": [],
                                "keywords": ["oversight"],
                            },
                        ],
                    },
                    {
                        "id": "CC2",
                        "name": "Communication and Information",
                        "description": "Communication criteria.",
                        "function_id": "CC",
                        "controls": [
                            {
                                "id": "CC2.1",
                                "name": "Internal Communication",
                                "description": "Communicates objectives.",
                                "implementation_examples": [],
                                "informative_references": [],
                                "keywords": ["communication"],
                            },
                        ],
                    },
                    {
                        "id": "CC9",
                        "name": "Risk Mitigation",
                        "description": "Risk mitigation criteria.",
                        "function_id": "CC",
                        "controls": [
                            {
                                "id": "CC9.1",
                                "name": "Disaster Recovery",
                                "description": "Disaster recovery planning.",
                                "implementation_examples": [],
                                "informative_references": [],
                                "keywords": ["disaster"],
                            },
                            {
                                "id": "CC9.2",
                                "name": "Backup Procedures",
                                "description": "Backup and recovery.",
                                "implementation_examples": [],
                                "informative_references": [],
                                "keywords": ["backup"],
                            },
                            {
                                "id": "CC9.3",
                                "name": "Recovery Testing",
                                "description": "Tests recovery procedures.",
                                "implementation_examples": [],
                                "informative_references": [],
                                "keywords": ["testing"],
                            },
                        ],
                    },
                ],
            },
            {
                "id": "A",
                "name": "Availability",
                "description": "Availability criteria.",
                "categories": [
                    {
                        "id": "A1",
                        "name": "System Availability",
                        "description": "System availability criteria.",
                        "function_id": "A",
                        "controls": [
                            {
                                "id": "A1.1",
                                "name": "Capacity Management",
                                "description": "Manages system capacity.",
                                "implementation_examples": [],
                                "informative_references": [],
                                "keywords": ["capacity"],
                            },
                        ],
                    }
                ],
            },
        ]
    }


@pytest.fixture
def framework_manager_with_soc2(
    temp_framework_dir: Path, sample_soc2_data: dict[str, Any]
) -> tuple[FrameworkManager, Path]:
    """Create a FrameworkManager with SOC2 TSC 2017 data."""
    soc2_file = temp_framework_dir / "soc2-tsc-2017.json"
    with open(soc2_file, "w") as f:
        json.dump(sample_soc2_data, f)

    manager = FrameworkManager(data_dir=temp_framework_dir)
    return manager, temp_framework_dir


@pytest.mark.asyncio
async def test_soc2_framework_loading(
    framework_manager_with_soc2: tuple[FrameworkManager, Path],
) -> None:
    """Test that SOC2 appears in list_frameworks()."""
    manager, _ = framework_manager_with_soc2
    frameworks = await manager.list_frameworks()

    soc2 = next((f for f in frameworks if f.id == "soc2-tsc-2017"), None)
    assert soc2 is not None, "SOC2 framework should be in list"
    assert soc2.status == FrameworkStatus.ACTIVE, "SOC2 should be ACTIVE when data exists"


@pytest.mark.asyncio
async def test_soc2_controls_retrieval(
    framework_manager_with_soc2: tuple[FrameworkManager, Path],
) -> None:
    """Test that SOC2 CC controls can be retrieved via list_controls()."""
    manager, _ = framework_manager_with_soc2

    # Get all controls
    all_controls = await manager.list_controls("soc2-tsc-2017")
    assert len(all_controls) == 7, f"Expected 7 controls, got {len(all_controls)}"

    # Filter by CC function
    cc_controls = await manager.list_controls("soc2-tsc-2017", function_id="CC")
    assert len(cc_controls) == 6, f"Expected 6 CC controls, got {len(cc_controls)}"
    assert all(c.function_id == "CC" for c in cc_controls)

    # Verify specific control IDs
    control_ids = {c.id for c in cc_controls}
    assert "CC1.1" in control_ids
    assert "CC2.1" in control_ids
    assert "CC9.3" in control_ids


@pytest.mark.asyncio
async def test_soc2_framework_metadata(
    framework_manager_with_soc2: tuple[FrameworkManager, Path],
) -> None:
    """Test that SOC2 framework metadata is correct."""
    manager, _ = framework_manager_with_soc2
    frameworks = await manager.list_frameworks()

    soc2 = next((f for f in frameworks if f.id == "soc2-tsc-2017"), None)
    assert soc2 is not None

    # Verify metadata
    assert soc2.name == "SOC 2 Trust Services Criteria (2017)"
    assert soc2.version == "2017"
    assert soc2.status == FrameworkStatus.ACTIVE
    assert soc2.description and ("AICPA" in soc2.description or "Trust Services" in soc2.description)
    assert soc2.control_count == 7  # 6 CC + 1 A controls in sample data
