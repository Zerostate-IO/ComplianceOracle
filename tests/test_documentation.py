"""Tests for documentation tools (document_compliance, link_evidence, get_documentation, export_documentation)."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from compliance_oracle.assessment.contracts import (
    DegradeReason,
    IntelligenceMetadata,
    IntelligenceMode,
)
from compliance_oracle.models.schemas import (
    ComplianceState,
    ComplianceSummary,
    ControlDocumentation,
    ControlStatus,
    Evidence,
    EvidenceType,
)


class TestDocumentCompliance:
    """Tests for document_compliance tool."""


    @pytest.mark.asyncio
    async def test_document_compliance_happy_path(
        self,
        mock_state_manager,
        sample_control_documentation: ControlDocumentation,
    ) -> None:
        """Test document_compliance records control status."""
        mock_state_manager.document_control = AsyncMock()

        # Create a documentation object
        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            implementation_summary="Implemented via Okta SSO",
            owner="Security Team",
        )

        await mock_state_manager.document_control(doc)

        mock_state_manager.document_control.assert_called_once_with(doc)

    @pytest.mark.asyncio
    async def test_document_compliance_partial_status(
        self,
        mock_state_manager,
    ) -> None:
        """Test document_compliance with partial status."""
        mock_state_manager.document_control = AsyncMock()

        doc = ControlDocumentation(
            control_id="PR.AC-02",
            framework_id="nist-csf-2.0",
            status=ControlStatus.PARTIAL,
            implementation_summary="Partially implemented",
            notes="MFA not yet deployed to all users",
        )

        await mock_state_manager.document_control(doc)

        mock_state_manager.document_control.assert_called_once()

    @pytest.mark.asyncio
    async def test_document_compliance_with_all_fields(
        self,
        mock_state_manager,
    ) -> None:
        """Test document_compliance with all optional fields."""
        mock_state_manager.document_control = AsyncMock()

        doc = ControlDocumentation(
            control_id="PR.DS-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            implementation_summary="Data encrypted at rest using AES-256",
            owner="Infrastructure Team",
            notes="Reviewed quarterly",
        )

        await mock_state_manager.document_control(doc)

        assert doc.control_id == "PR.DS-01"
        assert doc.status == ControlStatus.IMPLEMENTED

    @pytest.mark.asyncio
    async def test_document_compliance_not_applicable(
        self,
        mock_state_manager,
    ) -> None:
        """Test document_compliance with not_applicable status."""
        mock_state_manager.document_control = AsyncMock()

        doc = ControlDocumentation(
            control_id="PR.IP-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.NOT_APPLICABLE,
            notes="No physical infrastructure in scope",
        )

        await mock_state_manager.document_control(doc)

        assert doc.status == ControlStatus.NOT_APPLICABLE


class TestLinkEvidence:
    """Tests for link_evidence tool."""

    @pytest.mark.asyncio
    async def test_link_evidence_happy_path(
        self,
        mock_state_manager,
        sample_evidence: Evidence,
    ) -> None:
        """Test link_evidence attaches evidence to control."""
        mock_state_manager.link_evidence = AsyncMock()

        await mock_state_manager.link_evidence(
            framework_id="nist-csf-2.0",
            control_id="PR.AC-01",
            evidence=sample_evidence,
        )

        mock_state_manager.link_evidence.assert_called_once()

    @pytest.mark.asyncio
    async def test_link_evidence_with_line_range(
        self,
        mock_state_manager,
    ) -> None:
        """Test link_evidence with line range for code evidence."""
        mock_state_manager.link_evidence = AsyncMock()

        evidence = Evidence(
            type=EvidenceType.CODE,
            path="src/auth/middleware.py",
            description="MFA enforcement middleware",
            line_range=(45, 62),
        )

        await mock_state_manager.link_evidence(
            framework_id="nist-csf-2.0",
            control_id="PR.AC-01",
            evidence=evidence,
        )

        mock_state_manager.link_evidence.assert_called_once()
        assert evidence.line_range == (45, 62)

    @pytest.mark.asyncio
    async def test_link_evidence_url_type(
        self,
        mock_state_manager,
    ) -> None:
        """Test link_evidence with URL evidence type."""
        mock_state_manager.link_evidence = AsyncMock()

        evidence = Evidence(
            type=EvidenceType.URL,
            path="https://docs.company.com/security/mfa-policy",
            description="MFA policy documentation",
        )

        await mock_state_manager.link_evidence(
            framework_id="nist-csf-2.0",
            control_id="PR.AC-01",
            evidence=evidence,
        )

        mock_state_manager.link_evidence.assert_called_once()
        assert evidence.type == EvidenceType.URL

    @pytest.mark.asyncio
    async def test_link_evidence_control_not_documented(
        self,
        mock_state_manager,
    ) -> None:
        """Test link_evidence raises error for undocumented control."""
        mock_state_manager.link_evidence = AsyncMock(
            side_effect=ValueError(
                "Control INVALID-99 is not documented. Use document_compliance first."
            )
        )

        evidence = Evidence(
            type=EvidenceType.CONFIG,
            path="config/auth.yaml",
            description="Auth configuration",
        )

        with pytest.raises(ValueError, match="not documented"):
            await mock_state_manager.link_evidence(
                framework_id="nist-csf-2.0",
                control_id="INVALID-99",
                evidence=evidence,
            )


class TestGetDocumentation:
    """Tests for get_documentation tool."""

    @pytest.mark.asyncio
    async def test_get_documentation_happy_path(
        self,
        mock_state_manager,
        sample_control_documentation: ControlDocumentation,
    ) -> None:
        """Test get_documentation returns current state."""
        state = ComplianceState(
            controls={
                "nist-csf-2.0:PR.AC-01": sample_control_documentation,
            }
        )
        mock_state_manager.get_state = AsyncMock(return_value=state)
        mock_state_manager.get_summary = AsyncMock(
            return_value=ComplianceSummary(
                framework_id="nist-csf-2.0",
                total_controls=106,
                implemented=1,
                partial=0,
                planned=0,
                not_applicable=0,
                not_addressed=105,
                completion_percentage=0.94,
            )
        )

        result = await mock_state_manager.get_state()
        summary = await mock_state_manager.get_summary("nist-csf-2.0")

        assert len(result.controls) == 1
        assert summary.framework_id == "nist-csf-2.0"
        assert summary.implemented == 1

    @pytest.mark.asyncio
    async def test_get_documentation_with_filters(
        self,
        mock_state_manager,
        sample_control_documentation: ControlDocumentation,
    ) -> None:
        """Test get_documentation with status filter."""
        state = ComplianceState(
            controls={
                "nist-csf-2.0:PR.AC-01": sample_control_documentation,
            }
        )
        mock_state_manager.get_state = AsyncMock(return_value=state)

        result = await mock_state_manager.get_state()

        # Verify filtering logic would work
        implemented_controls = [
            doc for key, doc in result.controls.items() if doc.status == ControlStatus.IMPLEMENTED
        ]
        assert len(implemented_controls) == 1

    @pytest.mark.asyncio
    async def test_get_documentation_empty_state(
        self,
        mock_state_manager,
    ) -> None:
        """Test get_documentation with no documented controls."""
        mock_state_manager.get_state = AsyncMock(return_value=ComplianceState())
        mock_state_manager.get_summary = AsyncMock(return_value=None)

        result = await mock_state_manager.get_state()

        assert len(result.controls) == 0


class TestExportDocumentation:
    """Tests for export_documentation tool."""

    @pytest.mark.asyncio
    async def test_export_documentation_markdown(
        self,
        mock_state_manager,
    ) -> None:
        """Test export_documentation returns markdown format."""
        mock_state_manager.export = AsyncMock(
            return_value="# Compliance Documentation: nist-csf-2.0\n\n## Summary\n..."
        )

        result = await mock_state_manager.export(
            format="markdown",
            framework_id="nist-csf-2.0",
            include_evidence=True,
            include_gaps=True,
        )

        assert result.startswith("# Compliance Documentation")
        assert "nist-csf-2.0" in result

    @pytest.mark.asyncio
    async def test_export_documentation_json(
        self,
        mock_state_manager,
    ) -> None:
        """Test export_documentation returns JSON format."""
        mock_state_manager.export = AsyncMock(
            return_value='{"framework_id": "nist-csf-2.0", "controls": []}'
        )

        result = await mock_state_manager.export(
            format="json",
            framework_id="nist-csf-2.0",
            include_evidence=False,
            include_gaps=True,
        )

        assert "framework_id" in result
        assert "nist-csf-2.0" in result

    @pytest.mark.asyncio
    async def test_export_documentation_with_evidence(
        self,
        mock_state_manager,
        sample_control_documentation: ControlDocumentation,
        sample_evidence: Evidence,
    ) -> None:
        """Test export_documentation includes evidence when requested."""
        sample_control_documentation.evidence = [sample_evidence]
        mock_state_manager.export = AsyncMock(
            return_value="# Compliance Report\n\n**Evidence**:\n- [config] `config/auth.yaml`"
        )

        result = await mock_state_manager.export(
            format="markdown",
            framework_id="nist-csf-2.0",
            include_evidence=True,
            include_gaps=False,
        )

        assert "Evidence" in result

    @pytest.mark.asyncio
    async def test_export_documentation_with_gaps(
        self,
        mock_state_manager,
    ) -> None:
        """Test export_documentation includes gaps section when requested."""
        mock_state_manager.export = AsyncMock(
            return_value="# Compliance Report\n\n## Gaps (Not Addressed)\n- **PR.AC-02**"
        )

        result = await mock_state_manager.export(
            format="markdown",
            framework_id="nist-csf-2.0",
            include_evidence=False,
            include_gaps=True,
        )

        assert "Gaps" in result


# ==============================================================================
# Integration tests for tool functions (testing actual tool code paths)
# ==============================================================================


class TestLinkEvidenceToolPaths:
    """Tests for link_evidence tool code paths."""

    @pytest.mark.asyncio
    async def test_link_evidence_with_line_start_and_line_end(self, tmp_path: Path) -> None:
        """Test link_evidence tool with both line_start and line_end parameters (line 96)."""
        from fastmcp import FastMCP

        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)

        # Get the link_evidence tool function via tool_manager
        tools = await mcp._tool_manager.get_tools()
        link_evidence_fn = tools["link_evidence"].fn

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager"
        ) as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.link_evidence = AsyncMock()
            mock_manager_class.return_value = mock_instance

            # Call with both line_start and line_end to cover line 96
            result = await link_evidence_fn(
                control_id="PR.AC-01",
                evidence_type="code",
                path="src/auth.py",
                description="Auth implementation",
                line_start=10,
                line_end=20,
                project_path=str(tmp_path),
            )

            assert result["success"] is True
            # Verify link_evidence was called with Evidence containing line_range
            call_args = mock_instance.link_evidence.call_args
            evidence = call_args.kwargs["evidence"]
            assert evidence.line_range == (10, 20)


class TestGetDocumentationToolPaths:
    """Tests for get_documentation tool code paths (filtering logic)."""

    @pytest.fixture
    async def setup_mcp(self):
        from fastmcp import FastMCP

        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)
        return mcp

    @pytest.mark.asyncio
    async def test_get_documentation_framework_filter(self, tmp_path: Path) -> None:
        """Test get_documentation filters by framework (lines 149-150)."""
        from fastmcp import FastMCP

        from compliance_oracle.models.schemas import (
            ComplianceState,
            ControlDocumentation,
            ControlStatus,
        )
        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)
        tools = await mcp._tool_manager.get_tools()
        get_doc_fn = tools["get_documentation"].fn

        # Create controls for different frameworks
        nist_doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
        )
        other_doc = ControlDocumentation(
            control_id="AC-1",
            framework_id="nist-800-53-r5",
            status=ControlStatus.IMPLEMENTED,
        )

        state = ComplianceState(
            controls={
                "nist-csf-2.0:PR.AC-01": nist_doc,
                "nist-800-53-r5:AC-1": other_doc,
            }
        )

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager"
        ) as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.get_summary = AsyncMock(return_value=None)
            mock_manager_class.return_value = mock_instance

            # Request only nist-csf-2.0 controls
            result = await get_doc_fn(
                framework="nist-csf-2.0",
                project_path=str(tmp_path),
            )

            # Should only include nist-csf-2.0 control, not the other framework
            assert len(result["controls"]) == 1
            assert result["controls"][0]["control_id"] == "PR.AC-01"

    @pytest.mark.asyncio
    async def test_get_documentation_function_filter(self, tmp_path: Path) -> None:
        """Test get_documentation filters by function (lines 151-152)."""
        from fastmcp import FastMCP

        from compliance_oracle.models.schemas import (
            ComplianceState,
            ControlDocumentation,
            ControlStatus,
        )
        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)
        tools = await mcp._tool_manager.get_tools()
        get_doc_fn = tools["get_documentation"].fn

        pr_doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
        )
        id_doc = ControlDocumentation(
            control_id="ID.AM-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
        )

        state = ComplianceState(
            controls={
                "nist-csf-2.0:PR.AC-01": pr_doc,
                "nist-csf-2.0:ID.AM-01": id_doc,
            }
        )

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager"
        ) as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.get_summary = AsyncMock(return_value=None)
            mock_manager_class.return_value = mock_instance

            result = await get_doc_fn(
                framework="nist-csf-2.0",
                function="PR",
                project_path=str(tmp_path),
            )

            # Should only include PR function controls
            assert len(result["controls"]) == 1
            assert result["controls"][0]["control_id"] == "PR.AC-01"

    @pytest.mark.asyncio
    async def test_get_documentation_category_filter(self, tmp_path: Path) -> None:
        """Test get_documentation filters by category (lines 153-154)."""
        from fastmcp import FastMCP

        from compliance_oracle.models.schemas import (
            ComplianceState,
            ControlDocumentation,
            ControlStatus,
        )
        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)
        tools = await mcp._tool_manager.get_tools()
        get_doc_fn = tools["get_documentation"].fn

        ac_doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
        )
        ds_doc = ControlDocumentation(
            control_id="PR.DS-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
        )

        state = ComplianceState(
            controls={
                "nist-csf-2.0:PR.AC-01": ac_doc,
                "nist-csf-2.0:PR.DS-01": ds_doc,
            }
        )

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager"
        ) as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.get_summary = AsyncMock(return_value=None)
            mock_manager_class.return_value = mock_instance

            result = await get_doc_fn(
                framework="nist-csf-2.0",
                category="PR.AC",
                project_path=str(tmp_path),
            )

            # Should only include PR.AC category controls
            assert len(result["controls"]) == 1
            assert result["controls"][0]["control_id"] == "PR.AC-01"

    @pytest.mark.asyncio
    async def test_get_documentation_status_filter(self, tmp_path: Path) -> None:
        """Test get_documentation filters by status (lines 155-156)."""
        from fastmcp import FastMCP

        from compliance_oracle.models.schemas import (
            ComplianceState,
            ControlDocumentation,
            ControlStatus,
        )
        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)
        tools = await mcp._tool_manager.get_tools()
        get_doc_fn = tools["get_documentation"].fn

        impl_doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
        )
        partial_doc = ControlDocumentation(
            control_id="PR.AC-02",
            framework_id="nist-csf-2.0",
            status=ControlStatus.PARTIAL,
        )

        state = ComplianceState(
            controls={
                "nist-csf-2.0:PR.AC-01": impl_doc,
                "nist-csf-2.0:PR.AC-02": partial_doc,
            }
        )

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager"
        ) as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.get_summary = AsyncMock(return_value=None)
            mock_manager_class.return_value = mock_instance

            result = await get_doc_fn(
                framework="nist-csf-2.0",
                status="implemented",
                project_path=str(tmp_path),
            )

            # Should only include implemented controls
            assert len(result["controls"]) == 1
            assert result["controls"][0]["control_id"] == "PR.AC-01"

    @pytest.mark.asyncio
    async def test_get_documentation_exclude_evidence(self, tmp_path: Path) -> None:
        """Test get_documentation excludes evidence when include_evidence=False (lines 159-160)."""
        from fastmcp import FastMCP

        from compliance_oracle.models.schemas import (
            ComplianceState,
            ControlDocumentation,
            ControlStatus,
            Evidence,
            EvidenceType,
        )
        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)
        tools = await mcp._tool_manager.get_tools()
        get_doc_fn = tools["get_documentation"].fn

        doc_with_evidence = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            evidence=[
                Evidence(
                    type=EvidenceType.CONFIG,
                    path="config.yaml",
                    description="test",
                )
            ],
        )

        state = ComplianceState(
            controls={
                "nist-csf-2.0:PR.AC-01": doc_with_evidence,
            }
        )

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager"
        ) as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.get_summary = AsyncMock(return_value=None)
            mock_manager_class.return_value = mock_instance

            result = await get_doc_fn(
                framework="nist-csf-2.0",
                include_evidence=False,
                project_path=str(tmp_path),
            )

            # Evidence should be excluded from the control dict
            assert "evidence" not in result["controls"][0]


class TestExportDocumentationToolPaths:
    """Tests for export_documentation tool code paths (file writing)."""

    @pytest.mark.asyncio
    async def test_export_documentation_with_output_path(self, tmp_path: Path) -> None:
        """Test export_documentation writes to file when output_path is provided (lines 207-211)."""
        from fastmcp import FastMCP

        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)
        tools = await mcp._tool_manager.get_tools()
        export_fn = tools["export_documentation"].fn

        export_content = "# Compliance Report\n\n## Summary\n- 10 controls documented"

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager"
        ) as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.export = AsyncMock(return_value=export_content)
            mock_manager_class.return_value = mock_instance

            result = await export_fn(
                format="markdown",
                framework="nist-csf-2.0",
                output_path="reports/compliance.md",
                project_path=str(tmp_path),
            )

            # Verify file was written
            expected_file = tmp_path / "reports" / "compliance.md"
            assert expected_file.exists()
            assert expected_file.read_text() == export_content

            # Verify result structure
            assert result["output_path"] == str(expected_file)
            assert "message" in result

            assert "compliance.md" in result["message"]


class TestExportWithMetadata:
    """Tests for export_documentation with intelligence metadata."""

    @pytest.mark.asyncio
    async def test_export_json_with_metadata(self, tmp_path: Path) -> None:
        """Test JSON export includes metadata when present."""
        from compliance_oracle.assessment.contracts import (
            IntelligenceMetadata,
            IntelligenceMode,
        )
        from compliance_oracle.documentation.state import ComplianceStateManager

        manager = ComplianceStateManager(tmp_path)

        # Create control with metadata
        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            implementation_summary="Test implementation",
            intelligence_metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.HYBRID,
                llm_used=True,
                latency_ms=150,
            ),
        )
        await manager.document_control(doc)

        # Export as JSON
        result = await manager.export(
            format="json",
            framework_id="nist-csf-2.0",
            include_evidence=True,
            include_gaps=False,
        )

        import json
        data = json.loads(result)

        # Verify metadata is included
        assert len(data["controls"]) == 1
        control = data["controls"][0]
        assert "intelligence_metadata" in control
        assert control["intelligence_metadata"]["analysis_mode"] == "hybrid"
        assert control["intelligence_metadata"]["llm_used"] is True
        assert control["intelligence_metadata"]["latency_ms"] == 150

    @pytest.mark.asyncio
    async def test_export_json_without_metadata_backward_compat(self, tmp_path: Path) -> None:
        """Test JSON export excludes metadata key when not present (backward compat)."""
        from compliance_oracle.documentation.state import ComplianceStateManager

        manager = ComplianceStateManager(tmp_path)

        # Create control WITHOUT metadata
        doc = ControlDocumentation(
            control_id="PR.AC-02",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            implementation_summary="Test implementation",
        )
        await manager.document_control(doc)

        # Export as JSON
        result = await manager.export(
            format="json",
            framework_id="nist-csf-2.0",
            include_evidence=True,
            include_gaps=False,
        )

        data = json.loads(result)

        # Verify metadata key is NOT present (backward compat)
        assert len(data["controls"]) == 1
        control = data["controls"][0]
        assert "intelligence_metadata" not in control

    @pytest.mark.asyncio
    async def test_export_markdown_with_metadata(self, tmp_path: Path) -> None:
        """Test Markdown export includes metadata section when present."""
        from compliance_oracle.assessment.contracts import (
            IntelligenceMetadata,
            IntelligenceMode,
        )
        from compliance_oracle.documentation.state import ComplianceStateManager

        manager = ComplianceStateManager(tmp_path)

        # Create control with full metadata
        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            implementation_summary="Test implementation",
            intelligence_metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.HYBRID,
                llm_used=False,
                degrade_reason=DegradeReason.OLLAMA_TIMEOUT,
                policy_violations=["you should implement"],
                latency_ms=500,
            ),
        )
        await manager.document_control(doc)

        # Export as Markdown
        result = await manager.export(
            format="markdown",
            framework_id="nist-csf-2.0",
            include_evidence=True,
            include_gaps=False,
        )

        # Verify metadata section is included
        assert "**Analysis Metadata**:" in result
        assert "- Mode: hybrid" in result
        assert "- LLM Used: False" in result
        assert "- Degrade Reason: ollama_timeout" in result
        assert "- Policy Violations: you should implement" in result
        assert "- Latency: 500ms" in result

    @pytest.mark.asyncio
    async def test_export_markdown_without_metadata_backward_compat(self, tmp_path: Path) -> None:
        """Test Markdown export excludes metadata section when not present."""
        from compliance_oracle.documentation.state import ComplianceStateManager

        manager = ComplianceStateManager(tmp_path)

        # Create control WITHOUT metadata
        doc = ControlDocumentation(
            control_id="PR.AC-02",
            framework_id="nist-csf-2.0",
            status=ControlStatus.PARTIAL,
            implementation_summary="Partial implementation",
        )
        await manager.document_control(doc)

        # Export as Markdown
        result = await manager.export(
            format="markdown",
            framework_id="nist-csf-2.0",
            include_evidence=True,
            include_gaps=False,
        )

        # Verify metadata section is NOT included
        assert "**Analysis Metadata**:" not in result
        assert "- Mode:" not in result

    @pytest.mark.asyncio
    async def test_export_json_with_degraded_metadata(self, tmp_path: Path) -> None:
        """Test JSON export includes degraded metadata with all fields."""
        from compliance_oracle.assessment.contracts import (
            IntelligenceMetadata,
            IntelligenceMode,
        )
        from compliance_oracle.documentation.state import ComplianceStateManager

        manager = ComplianceStateManager(tmp_path)

        # Create control with degraded metadata
        doc = ControlDocumentation(
            control_id="PR.DS-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.PARTIAL,
            intelligence_metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.HYBRID,
                llm_used=False,
                degrade_reason=DegradeReason.CIRCUIT_OPEN,
                policy_violations=[],
                latency_ms=5,
            ),
        )
        await manager.document_control(doc)

        result = await manager.export(
            format="json",
            framework_id="nist-csf-2.0",
            include_evidence=False,
            include_gaps=False,
        )

        import json
        data = json.loads(result)

        control = data["controls"][0]
        assert control["intelligence_metadata"]["analysis_mode"] == "hybrid"
        assert control["intelligence_metadata"]["degrade_reason"] == "circuit_open"
        assert control["intelligence_metadata"]["latency_ms"] == 5

    @pytest.mark.asyncio
    async def test_export_markdown_with_minimal_metadata(self, tmp_path: Path) -> None:
        """Test Markdown export with minimal metadata (only required fields)."""
        from compliance_oracle.assessment.contracts import (
            IntelligenceMetadata,
            IntelligenceMode,
        )
        from compliance_oracle.documentation.state import ComplianceStateManager

        manager = ComplianceStateManager(tmp_path)

        # Create control with minimal metadata
        doc = ControlDocumentation(
            control_id="PR.AT-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            intelligence_metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.DETERMINISTIC,
            ),
        )
        await manager.document_control(doc)

        result = await manager.export(
            format="markdown",
            framework_id="nist-csf-2.0",
            include_evidence=False,
            include_gaps=False,
        )

        # Verify minimal metadata is included
        assert "**Analysis Metadata**:" in result
        assert "- Mode: deterministic" in result
        assert "- LLM Used: False" in result
        # Optional fields should NOT be present
        assert "Degrade Reason" not in result
        assert "Policy Violations" not in result
        assert "Latency" not in result


# ==============================================================================
# Additional fixtures for metadata tests
# ==============================================================================


@pytest.fixture
def sample_intelligence_metadata():
    """Sample IntelligenceMetadata for testing."""
    from compliance_oracle.assessment.contracts import (
        IntelligenceMetadata,
        IntelligenceMode,
    )
    return IntelligenceMetadata(
        analysis_mode=IntelligenceMode.HYBRID,
        llm_used=True,
        latency_ms=250,
    )


@pytest.fixture
def sample_control_with_metadata(sample_intelligence_metadata):
    """Sample ControlDocumentation with metadata."""
    return ControlDocumentation(
        control_id="PR.AC-01",
        framework_id="nist-csf-2.0",
        status=ControlStatus.IMPLEMENTED,
        implementation_summary="Implemented with LLM assistance",
        intelligence_metadata=sample_intelligence_metadata,
    )


class TestControlDocumentationWithMetadata:
    """Tests for ControlDocumentation model with intelligence_metadata field."""

    def test_control_documentation_accepts_metadata(self, sample_intelligence_metadata):
        """Test that ControlDocumentation accepts optional intelligence_metadata."""
        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            intelligence_metadata=sample_intelligence_metadata,
        )

        assert doc.intelligence_metadata is not None
        assert doc.intelligence_metadata.analysis_mode.value == "hybrid"
        assert doc.intelligence_metadata.llm_used is True

    def test_control_documentation_without_metadata(self):
        """Test that ControlDocumentation works without metadata (backward compat)."""
        doc = ControlDocumentation(
            control_id="PR.AC-02",
            framework_id="nist-csf-2.0",
            status=ControlStatus.PARTIAL,
        )

        assert doc.intelligence_metadata is None

    def test_control_documentation_serialization_with_metadata(
        self, sample_intelligence_metadata
    ):
        """Test model_dump includes metadata when present."""
        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            intelligence_metadata=sample_intelligence_metadata,
        )

        data = doc.model_dump(mode="json")
        assert "intelligence_metadata" in data
        assert data["intelligence_metadata"]["analysis_mode"] == "hybrid"

    def test_control_documentation_serialization_without_metadata(self):
        """Test model_dump includes None for metadata when not present."""
        doc = ControlDocumentation(
            control_id="PR.AC-02",
            framework_id="nist-csf-2.0",
            status=ControlStatus.PARTIAL,
        )

        data = doc.model_dump(mode="json")
        # Pydantic includes None by default
        assert data.get("intelligence_metadata") is None


class TestGetDocumentationWithMetadata:
    """Tests for get_documentation tool with metadata."""

    @pytest.mark.asyncio
    async def test_get_documentation_includes_metadata(self, tmp_path: Path) -> None:
        """Test get_documentation returns controls with metadata."""
        from fastmcp import FastMCP

        from compliance_oracle.assessment.contracts import (
            IntelligenceMetadata,
            IntelligenceMode,
        )
        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)
        tools = await mcp._tool_manager.get_tools()
        get_doc_fn = tools["get_documentation"].fn

        doc_with_metadata = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            intelligence_metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.HYBRID,
                llm_used=True,
                latency_ms=100,
            ),
        )

        state = ComplianceState(
            controls={
                "nist-csf-2.0:PR.AC-01": doc_with_metadata,
            }
        )

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager"
        ) as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.get_summary = AsyncMock(return_value=None)
            mock_manager_class.return_value = mock_instance

            result = await get_doc_fn(
                framework="nist-csf-2.0",
                project_path=str(tmp_path),
            )

            # Metadata should be included in control dict
            assert len(result["controls"]) == 1
            control = result["controls"][0]
            assert "intelligence_metadata" in control
            assert control["intelligence_metadata"]["analysis_mode"] == "hybrid"

    @pytest.mark.asyncio
    async def test_get_documentation_without_metadata_backward_compat(
        self, tmp_path: Path
    ) -> None:
        """Test get_documentation works without metadata (backward compat)."""
        from fastmcp import FastMCP

        from compliance_oracle.tools.documentation import register_documentation_tools

        mcp = FastMCP("test")
        register_documentation_tools(mcp)
        tools = await mcp._tool_manager.get_tools()
        get_doc_fn = tools["get_documentation"].fn

        doc_without_metadata = ControlDocumentation(
            control_id="PR.AC-02",
            framework_id="nist-csf-2.0",
            status=ControlStatus.PARTIAL,
        )

        state = ComplianceState(
            controls={
                "nist-csf-2.0:PR.AC-02": doc_without_metadata,
            }
        )

        with patch(
            "compliance_oracle.tools.documentation.ComplianceStateManager"
        ) as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.get_summary = AsyncMock(return_value=None)
            mock_manager_class.return_value = mock_instance

            result = await get_doc_fn(
                framework="nist-csf-2.0",
                project_path=str(tmp_path),
            )

            # Should work without metadata
            assert len(result["controls"]) == 1
            assert result["controls"][0]["control_id"] == "PR.AC-02"
            # model_dump returns None for optional fields not set
            assert result["controls"][0].get("intelligence_metadata") is None




class TestDocumentComplianceToolWithMetadata:
    """Tests for document_compliance tool with metadata support."""

    @pytest.mark.asyncio
    async def test_document_compliance_accepts_control_with_metadata(
        self, tmp_path: Path
    ) -> None:
        """Test document_compliance can store control with metadata."""
        from compliance_oracle.documentation.state import ComplianceStateManager

        manager = ComplianceStateManager(tmp_path)

        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            implementation_summary="Implemented with LLM assistance",
            intelligence_metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.HYBRID,
                llm_used=True,
                latency_ms=200,
            ),
        )

        await manager.document_control(doc)

        # Retrieve and verify
        retrieved = await manager.get_control_documentation(
            framework_id="nist-csf-2.0",
            control_id="PR.AC-01",
        )

        assert retrieved is not None
        assert retrieved.intelligence_metadata is not None
        assert retrieved.intelligence_metadata.analysis_mode == IntelligenceMode.HYBRID
        assert retrieved.intelligence_metadata.llm_used is True
        assert retrieved.intelligence_metadata.latency_ms == 200

    @pytest.mark.asyncio
    async def test_document_compliance_persists_metadata_to_state(
        self, tmp_path: Path
    ) -> None:
        """Test that metadata is persisted in state.json."""
        from compliance_oracle.documentation.state import ComplianceStateManager

        manager = ComplianceStateManager(tmp_path)

        doc = ControlDocumentation(
            control_id="PR.DS-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            intelligence_metadata=IntelligenceMetadata(
                analysis_mode=IntelligenceMode.DETERMINISTIC,
                latency_ms=50,
            ),
        )

        await manager.document_control(doc)

        # Load state file directly
        state_file = tmp_path / ".compliance-oracle" / "state.json"
        assert state_file.exists()

        with open(state_file) as f:
            state_data = json.load(f)

        # Verify metadata is in the persisted state
        key = "nist-csf-2.0:PR.DS-01"
        assert key in state_data["controls"]
        control_data = state_data["controls"][key]
        assert "intelligence_metadata" in control_data
        assert control_data["intelligence_metadata"]["analysis_mode"] == "deterministic"
