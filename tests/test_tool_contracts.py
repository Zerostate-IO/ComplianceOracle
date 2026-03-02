"""Tool contract smoke tests - validate response schema for all 13 MCP tools.

These tests verify that each tool function returns a response conforming to
its documented schema with required keys and correct types. They do NOT test
internal logic or edge cases - those are covered in dedicated test files.

Test Categories:
- [CONTRACT] - Response shape validation (keys and types)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP

from compliance_oracle.models.schemas import (
    AssessmentTemplate,
    ControlDetails,
    GapAnalysisResult,
    ListControlsResponse,
    ListFrameworksResponse,
    SearchResponse,
)


# ============================================================================
# LOOKUP TOOLS (3 tools)
# ============================================================================


class TestListFrameworksContract:
    """Contract tests for list_frameworks tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_list_frameworks(
        self,
        mock_framework_manager,
        sample_framework_info,
    ) -> None:
        """[CONTRACT] list_frameworks returns ListFrameworksResponse with frameworks key."""
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.lookup.FrameworkManager",
            return_value=mock_framework_manager,
        ):
            mock_framework_manager.list_frameworks.return_value = [sample_framework_info]

            # Register the tools
            from compliance_oracle.tools.lookup import register_lookup_tools

            register_lookup_tools(mcp)

            # Get the tool and call its underlying function
            tool = await mcp.get_tool("list_frameworks")
            result = await tool.fn()

            # Assert response is not None
            assert result is not None

            # Assert response is correct type
            assert isinstance(result, ListFrameworksResponse)

            # Assert required key exists
            assert hasattr(result, "frameworks")
            assert isinstance(result.frameworks, list)

            # Assert list contains expected type
            if result.frameworks:
                assert hasattr(result.frameworks[0], "id")
                assert hasattr(result.frameworks[0], "name")


class TestListControlsContract:
    """Contract tests for list_controls tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_list_controls(
        self,
        mock_framework_manager,
        sample_control,
    ) -> None:
        """[CONTRACT] list_controls returns ListControlsResponse with controls and framework_id keys."""
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.lookup.FrameworkManager",
            return_value=mock_framework_manager,
        ):
            mock_framework_manager.list_controls.return_value = [sample_control]

            from compliance_oracle.tools.lookup import register_lookup_tools

            register_lookup_tools(mcp)

            tool = await mcp.get_tool("list_controls")
            result = await tool.fn(framework="nist-csf-2.0")

            # Assert response is not None
            assert result is not None

            # Assert response is correct type
            assert isinstance(result, ListControlsResponse)

            # Assert required keys exist
            assert hasattr(result, "controls")
            assert hasattr(result, "framework_id")
            assert hasattr(result, "total_count")

            # Assert key types are correct
            assert isinstance(result.controls, list)
            assert isinstance(result.framework_id, str)
            assert isinstance(result.total_count, int)

            # Assert framework_id matches input
            assert result.framework_id == "nist-csf-2.0"


class TestGetControlDetailsContract:
    """Contract tests for get_control_details tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_get_control_details(
        self,
        mock_framework_manager,
        sample_control_details,
    ) -> None:
        """[CONTRACT] get_control_details returns ControlDetails with id, name, description keys."""
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.lookup.FrameworkManager",
            return_value=mock_framework_manager,
        ):
            mock_framework_manager.get_control_details.return_value = sample_control_details

            from compliance_oracle.tools.lookup import register_lookup_tools

            register_lookup_tools(mcp)

            tool = await mcp.get_tool("get_control_details")
            result = await tool.fn(
                control_id="PR.AC-01",
                framework="nist-csf-2.0",
            )

            # Assert response is not None
            assert result is not None

            # Assert response is correct type
            assert isinstance(result, ControlDetails)

            # Assert required keys exist
            assert hasattr(result, "id")
            assert hasattr(result, "name")
            assert hasattr(result, "description")
            assert hasattr(result, "framework_id")

            # Assert key types are correct
            assert isinstance(result.id, str)
            assert isinstance(result.name, str)
            assert isinstance(result.description, str)


# ============================================================================
# SEARCH TOOLS (2 tools)
# ============================================================================


class TestSearchControlsContract:
    """Contract tests for search_controls tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_search_controls(
        self,
        mock_control_searcher,
        sample_search_result,
    ) -> None:
        """[CONTRACT] search_controls returns SearchResponse with results and query keys."""
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.search.ControlSearcher",
            return_value=mock_control_searcher,
        ):
            mock_control_searcher.search.return_value = [sample_search_result]

            from compliance_oracle.tools.search import register_search_tools

            register_search_tools(mcp)

            tool = await mcp.get_tool("search_controls")
            result = await tool.fn(query="identity management")

            # Assert response is not None
            assert result is not None

            # Assert response is correct type
            assert isinstance(result, SearchResponse)

            # Assert required keys exist
            assert hasattr(result, "results")
            assert hasattr(result, "query")
            assert hasattr(result, "total_results")

            # Assert key types are correct
            assert isinstance(result.results, list)
            assert isinstance(result.query, str)
            assert isinstance(result.total_results, int)

            # Assert query matches input
            assert result.query == "identity management"


class TestGetControlContextContract:
    """Contract tests for get_control_context tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_get_control_context(
        self,
        mock_control_searcher,
        sample_control_details,
    ) -> None:
        """[CONTRACT] get_control_context returns dict with control, hierarchy, siblings, related keys."""
        mcp = FastMCP("test-server")

        expected_context = {
            "control": sample_control_details.model_dump(),
            "hierarchy": {
                "framework_id": "nist-csf-2.0",
                "function": {"id": "PR", "name": "PROTECT"},
                "category": {
                    "id": "PR.AC",
                    "name": "Identity Management and Access Control",
                },
            },
            "siblings": [{"id": "PR.AC-02", "name": "Physical Access"}],
            "related": [{"id": "PR.AC-03", "name": "Remote Access", "score": 0.85}],
        }

        with patch(
            "compliance_oracle.tools.search.ControlSearcher",
            return_value=mock_control_searcher,
        ):
            mock_control_searcher.get_context.return_value = expected_context

            from compliance_oracle.tools.search import register_search_tools

            register_search_tools(mcp)

            tool = await mcp.get_tool("get_control_context")
            result = await tool.fn(
                control_id="PR.AC-01",
                framework="nist-csf-2.0",
            )

            # Assert response is not None
            assert result is not None

            # Assert response is dict type
            assert isinstance(result, dict)

            # Assert required keys exist
            assert "control" in result
            assert "hierarchy" in result

            # Assert key types are correct
            assert isinstance(result["control"], dict)
            assert isinstance(result["hierarchy"], dict)


# ============================================================================
# DOCUMENTATION TOOLS (4 tools)
# ============================================================================


class TestDocumentComplianceContract:
    """Contract tests for document_compliance tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_document_compliance(
        self,
        mock_state_manager,
        tmp_path,
    ) -> None:
        """[CONTRACT] document_compliance returns dict with success, control_id, status keys."""
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager",
            return_value=mock_state_manager,
        ):
            mock_state_manager.document_control = AsyncMock()

            from compliance_oracle.tools.documentation import register_documentation_tools

            register_documentation_tools(mcp)

            tool = await mcp.get_tool("document_compliance")
            result = await tool.fn(
                control_id="PR.AC-01",
                status="implemented",
                framework="nist-csf-2.0",
                project_path=str(tmp_path),
            )

            # Assert response is not None
            assert result is not None

            # Assert response is dict type
            assert isinstance(result, dict)

            # Assert required keys exist
            assert "success" in result
            assert "control_id" in result
            assert "status" in result

            # Assert key types are correct
            assert isinstance(result["success"], bool)
            assert isinstance(result["control_id"], str)
            assert isinstance(result["status"], str)

            # Assert values match input
            assert result["success"] is True
            assert result["control_id"] == "PR.AC-01"
            assert result["status"] == "implemented"


class TestLinkEvidenceContract:
    """Contract tests for link_evidence tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_link_evidence(
        self,
        mock_state_manager,
        tmp_path,
    ) -> None:
        """[CONTRACT] link_evidence returns dict with success, control_id, evidence_type, path keys."""
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager",
            return_value=mock_state_manager,
        ):
            mock_state_manager.link_evidence = AsyncMock()

            from compliance_oracle.tools.documentation import register_documentation_tools

            register_documentation_tools(mcp)

            tool = await mcp.get_tool("link_evidence")
            result = await tool.fn(
                control_id="PR.AC-01",
                evidence_type="config",
                path="config/auth.yaml",
                description="MFA configuration",
                framework="nist-csf-2.0",
                project_path=str(tmp_path),
            )

            # Assert response is not None
            assert result is not None

            # Assert response is dict type
            assert isinstance(result, dict)

            # Assert required keys exist
            assert "success" in result
            assert "control_id" in result
            assert "evidence_type" in result
            assert "path" in result

            # Assert key types are correct
            assert isinstance(result["success"], bool)
            assert isinstance(result["control_id"], str)
            assert isinstance(result["evidence_type"], str)
            assert isinstance(result["path"], str)

            # Assert values match input
            assert result["control_id"] == "PR.AC-01"
            assert result["evidence_type"] == "config"
            assert result["path"] == "config/auth.yaml"


class TestGetDocumentationContract:
    """Contract tests for get_documentation tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_get_documentation(
        self,
        mock_state_manager,
        tmp_path,
    ) -> None:
        """[CONTRACT] get_documentation returns dict with framework, summary, controls keys."""
        from compliance_oracle.models.schemas import ComplianceState

        sample_state = ComplianceState()
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager",
            return_value=mock_state_manager,
        ):
            mock_state_manager.get_state.return_value = sample_state
            mock_state_manager.get_summary.return_value = None

            from compliance_oracle.tools.documentation import register_documentation_tools

            register_documentation_tools(mcp)

            tool = await mcp.get_tool("get_documentation")
            result = await tool.fn(
                framework="nist-csf-2.0",
                project_path=str(tmp_path),
            )

            # Assert response is not None
            assert result is not None

            # Assert response is dict type
            assert isinstance(result, dict)

            # Assert required keys exist
            assert "framework" in result
            assert "controls" in result

            # Assert key types are correct
            assert isinstance(result["framework"], str)
            assert isinstance(result["controls"], list)


class TestExportDocumentationContract:
    """Contract tests for export_documentation tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_export_documentation(
        self,
        mock_state_manager,
        tmp_path,
    ) -> None:
        """[CONTRACT] export_documentation returns dict with format, framework, content keys."""
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager",
            return_value=mock_state_manager,
        ):
            mock_state_manager.export.return_value = "# Compliance Report\n..."

            from compliance_oracle.tools.documentation import register_documentation_tools

            register_documentation_tools(mcp)

            tool = await mcp.get_tool("export_documentation")
            result = await tool.fn(
                format="markdown",
                framework="nist-csf-2.0",
                project_path=str(tmp_path),
            )

            # Assert response is not None
            assert result is not None

            # Assert response is dict type
            assert isinstance(result, dict)

            # Assert required keys exist
            assert "format" in result
            assert "framework" in result

            # Assert key types are correct
            assert isinstance(result["format"], str)
            assert isinstance(result["framework"], str)

            # When no output_path specified, content should be present
            assert "content" in result
            assert isinstance(result["content"], str)


# ============================================================================
# FRAMEWORK TOOLS (3 tools)
# ============================================================================


class TestCompareFrameworksContract:
    """Contract tests for compare_frameworks tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_compare_frameworks(self) -> None:
        """[CONTRACT] compare_frameworks returns dict with source and mappings keys."""
        mcp = FastMCP("test-server")
        mock_mapper = MagicMock()
        mock_mapper.get_mappings = AsyncMock(
            return_value=[
                {
                    "target_framework": "nist-800-53-r5",
                    "target_control_id": "IA-1",
                    "relationship": "equivalent",
                }
            ]
        )

        with patch(
            "compliance_oracle.tools.framework_mgmt.FrameworkMapper",
            return_value=mock_mapper,
        ):
            from compliance_oracle.tools.framework_mgmt import register_framework_tools

            register_framework_tools(mcp)

            tool = await mcp.get_tool("compare_frameworks")
            result = await tool.fn(
                control_id="PR.AC-01",
                source_framework="nist-csf-2.0",
            )

            # Assert response is not None
            assert result is not None

            # Assert response is dict type
            assert isinstance(result, dict)

            # Assert required keys exist
            assert "source" in result
            assert "mappings" in result

            # Assert key types are correct
            assert isinstance(result["source"], dict)
            assert isinstance(result["mappings"], list)


class TestGetGuidanceContract:
    """Contract tests for get_guidance tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_get_guidance(
        self,
        mock_framework_manager,
        sample_control_details,
    ) -> None:
        """[CONTRACT] get_guidance returns dict with control_id, control_name, description keys."""
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.framework_mgmt.FrameworkManager",
            return_value=mock_framework_manager,
        ):
            mock_framework_manager.get_control_details.return_value = sample_control_details

            from compliance_oracle.tools.framework_mgmt import register_framework_tools

            register_framework_tools(mcp)

            tool = await mcp.get_tool("get_guidance")
            result = await tool.fn(
                control_id="PR.AC-01",
                framework="nist-csf-2.0",
            )

            # Assert response is not None
            assert result is not None

            # Assert response is dict type
            assert isinstance(result, dict)

            # Assert required keys exist
            assert "control_id" in result
            assert "control_name" in result
            assert "description" in result

            # Assert key types are correct
            assert isinstance(result["control_id"], str)
            assert isinstance(result["control_name"], str)
            assert isinstance(result["description"], str)


class TestGetFrameworkGapContract:
    """Contract tests for get_framework_gap tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_get_framework_gap(self) -> None:
        """[CONTRACT] get_framework_gap returns GapAnalysisResult with gaps, summary keys."""
        mcp = FastMCP("test-server")
        mock_mapper = MagicMock()
        mock_mapper.analyze_gap = AsyncMock(
            return_value=GapAnalysisResult(
                current_framework="nist-csf-2.0",
                target_framework="nist-800-53-r5",
                already_covered=[],
                partially_covered=[],
                gaps=[],
                summary={
                    "total_target_controls": 0,
                    "fully_covered": 0,
                    "partially_covered": 0,
                    "gaps": 0,
                    "coverage_percentage": 0.0,
                },
            )
        )

        with patch(
            "compliance_oracle.tools.framework_mgmt.FrameworkMapper",
            return_value=mock_mapper,
        ):
            from compliance_oracle.tools.framework_mgmt import register_framework_tools

            register_framework_tools(mcp)

            tool = await mcp.get_tool("get_framework_gap")
            result = await tool.fn(
                current_framework="nist-csf-2.0",
                target_framework="nist-800-53-r5",
            )

            # Assert response is not None
            assert result is not None

            # Assert response is correct type
            assert isinstance(result, GapAnalysisResult)

            # Assert required keys exist
            assert hasattr(result, "gaps")
            assert hasattr(result, "summary")
            assert hasattr(result, "current_framework")
            assert hasattr(result, "target_framework")

            # Assert key types are correct
            assert isinstance(result.gaps, list)
            assert isinstance(result.summary, dict)
            assert isinstance(result.current_framework, str)
            assert isinstance(result.target_framework, str)


# ============================================================================
# ASSESSMENT TOOLS (1 tool)
# ============================================================================


class TestGetAssessmentQuestionsContract:
    """Contract tests for get_assessment_questions tool."""

    @pytest.mark.asyncio
    async def test_tool_contract_get_assessment_questions(
        self,
        mock_framework_manager,
        sample_control,
    ) -> None:
        """[CONTRACT] get_assessment_questions returns AssessmentTemplate with questions key."""
        mcp = FastMCP("test-server")

        with patch(
            "compliance_oracle.tools.assessment.FrameworkManager",
            return_value=mock_framework_manager,
        ):
            mock_framework_manager.list_controls.return_value = [sample_control]

            from compliance_oracle.tools.assessment import register_assessment_tools

            register_assessment_tools(mcp)

            tool = await mcp.get_tool("get_assessment_questions")
            result = await tool.fn(
                framework="nist-csf-2.0",
                function="PR",
            )

            # Assert response is not None
            assert result is not None

            # Assert response is correct type
            assert isinstance(result, AssessmentTemplate)

            # Assert required keys exist
            assert hasattr(result, "questions")
            assert hasattr(result, "framework_id")
            assert hasattr(result, "scope")

            # Assert key types are correct
            assert isinstance(result.questions, list)
            assert isinstance(result.framework_id, str)
            assert isinstance(result.scope, str)

            # Assert framework_id matches input
            assert result.framework_id == "nist-csf-2.0"

            # If questions exist, validate their structure
            if result.questions:
                question = result.questions[0]
                assert hasattr(question, "id")
                assert hasattr(question, "text")
                assert hasattr(question, "control_ids")
                assert hasattr(question, "answer_type")


# ============================================================================
# INTELLIGENCE CONTRACT TESTS
# ============================================================================


class TestIntelligenceContracts:
    """Contract tests for hybrid intelligence metadata and result models."""

    def test_intelligence_mode_enum_values(self) -> None:
        """[CONTRACT] IntelligenceMode enum has DETERMINISTIC and HYBRID values."""
        from compliance_oracle.assessment.contracts import IntelligenceMode

        assert IntelligenceMode.DETERMINISTIC.value == "deterministic"
        assert IntelligenceMode.HYBRID.value == "hybrid"

    def test_degrade_reason_enum_values(self) -> None:
        """[CONTRACT] DegradeReason enum has all expected error codes."""
        from compliance_oracle.assessment.contracts import DegradeReason

        assert DegradeReason.OLLAMA_TIMEOUT.value == "ollama_timeout"
        assert DegradeReason.OLLAMA_UNREACHABLE.value == "ollama_unreachable"
        assert DegradeReason.OLLAMA_MALFORMED_RESPONSE.value == "ollama_malformed_response"
        assert DegradeReason.CIRCUIT_OPEN.value == "circuit_open"
        assert DegradeReason.POLICY_VIOLATION.value == "policy_violation"

    def test_intelligence_metadata_defaults(self) -> None:
        """[CONTRACT] IntelligenceMetadata has correct defaults."""
        from compliance_oracle.assessment.contracts import (
            IntelligenceMetadata,
            IntelligenceMode,
        )

        metadata = IntelligenceMetadata()
        assert metadata.analysis_mode == IntelligenceMode.DETERMINISTIC
        assert metadata.llm_used is False
        assert metadata.degrade_reason is None
        assert metadata.policy_violations == []
        assert metadata.latency_ms is None

    def test_intelligence_metadata_serialization(self) -> None:
        """[CONTRACT] IntelligenceMetadata serializes correctly to JSON."""
        from compliance_oracle.assessment.contracts import (
            DegradeReason,
            IntelligenceMetadata,
            IntelligenceMode,
        )

        metadata = IntelligenceMetadata(
            analysis_mode=IntelligenceMode.HYBRID,
            llm_used=True,
            degrade_reason=DegradeReason.OLLAMA_TIMEOUT,
            policy_violations=["test_violation"],
            latency_ms=150,
        )

        data = metadata.model_dump(mode="json")

        assert data["analysis_mode"] == "hybrid"
        assert data["llm_used"] is True
        assert data["degrade_reason"] == "ollama_timeout"
        assert data["policy_violations"] == ["test_violation"]
        assert data["latency_ms"] == 150

    def test_intelligence_result_with_metadata(self) -> None:
        """[CONTRACT] IntelligenceResult can carry optional metadata."""
        from compliance_oracle.assessment.contracts import (
            DegradeReason,
            IntelligenceMetadata,
            IntelligenceMode,
            IntelligenceResult,
        )

        # Test with metadata
        result = IntelligenceResult(
            metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.HYBRID,
                llm_used=False,
                degrade_reason=DegradeReason.OLLAMA_UNREACHABLE,
            )
        )

        assert result.get_analysis_mode() == IntelligenceMode.HYBRID
        assert result.is_llm_used() is False
        assert result.get_degrade_reason() == DegradeReason.OLLAMA_UNREACHABLE

    def test_intelligence_result_without_metadata(self) -> None:
        """[CONTRACT] IntelligenceResult works without metadata (backward compat)."""
        from compliance_oracle.assessment.contracts import (
            IntelligenceMode,
            IntelligenceResult,
        )

        result = IntelligenceResult()

        assert result.metadata is None
        assert result.get_analysis_mode() == IntelligenceMode.DETERMINISTIC
        assert result.is_llm_used() is False
        assert result.get_degrade_reason() is None
        assert result.get_policy_violations() == []

    def test_invalid_analysis_mode_raises_error(self) -> None:
        """[CONTRACT] Invalid analysis_mode value raises validation error."""
        import pydantic

        from compliance_oracle.assessment.contracts import IntelligenceMetadata

        # This should raise a validation error
        with pytest.raises(pydantic.ValidationError):
            IntelligenceMetadata(analysis_mode="invalid_mode")  # type: ignore[arg-type]

    def test_create_deterministic_metadata_helper(self) -> None:
        """[CONTRACT] create_deterministic_metadata creates correct metadata."""
        from compliance_oracle.assessment.contracts import (
            IntelligenceMode,
            create_deterministic_metadata,
        )

        metadata = create_deterministic_metadata(latency_ms=100)

        assert metadata.analysis_mode == IntelligenceMode.DETERMINISTIC
        assert metadata.llm_used is False
        assert metadata.degrade_reason is None
        assert metadata.latency_ms == 100

    def test_create_hybrid_metadata_helper(self) -> None:
        """[CONTRACT] create_hybrid_metadata creates correct metadata."""
        from compliance_oracle.assessment.contracts import (
            DegradeReason,
            IntelligenceMode,
            create_hybrid_metadata,
        )

        metadata = create_hybrid_metadata(
            llm_used=True,
            policy_violations=["violation1"],
            latency_ms=200,
        )

        assert metadata.analysis_mode == IntelligenceMode.HYBRID
        assert metadata.llm_used is True
        assert metadata.policy_violations == ["violation1"]
        assert metadata.latency_ms == 200

    def test_create_degraded_metadata_helper(self) -> None:
        """[CONTRACT] create_degraded_metadata creates correct metadata."""
        from compliance_oracle.assessment.contracts import (
            DegradeReason,
            IntelligenceMode,
            create_degraded_metadata,
        )

        metadata = create_degraded_metadata(
            degrade_reason=DegradeReason.CIRCUIT_OPEN,
            policy_violations=["policy_check_failed"],
        )

        assert metadata.analysis_mode == IntelligenceMode.HYBRID
        assert metadata.llm_used is False  # Degraded means LLM wasn't used
        assert metadata.degrade_reason == DegradeReason.CIRCUIT_OPEN
        assert metadata.policy_violations == ["policy_check_failed"]

    def test_assessment_result_backward_compatible(self) -> None:
        """[CONTRACT] AssessmentResult works without metadata (backward compat)."""
        from compliance_oracle.models.schemas import AssessmentResult

        # Old-style result without metadata should still work
        result = AssessmentResult(
            control_id="PR.AC-01",
            control_name="Identity Management",
            framework_id="nist-csf-2.0",
            maturity_level="intermediate",
            strengths=["MFA implemented"],
            gaps=["No PAM solution"],
            recommendations=["PAM coverage may need assessment"],
        )

        assert result.control_id == "PR.AC-01"
        assert result.metadata is None  # Optional field defaults to None

    def test_assessment_result_with_metadata(self) -> None:
        """[CONTRACT] AssessmentResult can carry intelligence metadata."""
        from compliance_oracle.assessment.contracts import (
            DegradeReason,
            IntelligenceMetadata,
            IntelligenceMode,
        )
        from compliance_oracle.models.schemas import AssessmentResult

        # New-style result with metadata
        result = AssessmentResult(
            control_id="PR.AC-01",
            control_name="Identity Management",
            framework_id="nist-csf-2.0",
            maturity_level="intermediate",
            metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.HYBRID,
                llm_used=True,
                degrade_reason=DegradeReason.OLLAMA_TIMEOUT,
            ),
        )

        assert result.metadata is not None
        assert result.metadata.analysis_mode == IntelligenceMode.HYBRID
        assert result.metadata.llm_used is True

    def test_assessment_result_serialization_with_metadata(self) -> None:
        """[CONTRACT] AssessmentResult with metadata serializes correctly."""
        from compliance_oracle.assessment.contracts import (
            DegradeReason,
            IntelligenceMetadata,
            IntelligenceMode,
        )
        from compliance_oracle.models.schemas import AssessmentResult

        result = AssessmentResult(
            control_id="PR.AC-01",
            control_name="Identity Management",
            framework_id="nist-csf-2.0",
            maturity_level="intermediate",
            metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.DETERMINISTIC,
                llm_used=False,
                latency_ms=50,
            ),
        )

        data = result.model_dump(mode="json")

        assert data["control_id"] == "PR.AC-01"
        assert data["metadata"]["analysis_mode"] == "deterministic"
        assert data["metadata"]["llm_used"] is False
        assert data["metadata"]["latency_ms"] == 50
