"""Documentation mode tools for recording compliance state."""

from pathlib import Path

from fastmcp import FastMCP

from compliance_oracle.documentation.state import ComplianceStateManager
from compliance_oracle.models.schemas import (
    ComplianceState,
    ComplianceSummary,
    ControlDocumentation,
    ControlStatus,
    Evidence,
    EvidenceType,
)


def register_documentation_tools(mcp: FastMCP) -> None:
    """Register documentation tools with the MCP server."""

    @mcp.tool()
    async def document_compliance(
        control_id: str,
        status: str,
        framework: str = "nist-csf-2.0",
        implementation_summary: str | None = None,
        owner: str | None = None,
        notes: str | None = None,
        project_path: str = ".",
    ) -> dict:
        """Record that a control is satisfied (or partially satisfied).

        Args:
            control_id: Control identifier (e.g., 'PR.DS-02')
            status: Implementation status - one of:
                    'implemented', 'partial', 'planned', 'not_applicable', 'not_addressed'
            framework: Framework ID (default: 'nist-csf-2.0')
            implementation_summary: Brief description of how the control is satisfied
            owner: Team or person responsible
            notes: Additional notes or context
            project_path: Path to project root (default: current directory)

        Returns:
            Confirmation of documented control.
        """
        manager = ComplianceStateManager(Path(project_path))

        doc = ControlDocumentation(
            control_id=control_id,
            framework_id=framework,
            status=ControlStatus(status),
            implementation_summary=implementation_summary,
            owner=owner,
            notes=notes,
        )

        await manager.document_control(doc)

        return {
            "success": True,
            "control_id": control_id,
            "framework": framework,
            "status": status,
            "message": f"Control {control_id} documented as {status}",
        }

    @mcp.tool()
    async def link_evidence(
        control_id: str,
        evidence_type: str,
        path: str,
        description: str,
        framework: str = "nist-csf-2.0",
        line_start: int | None = None,
        line_end: int | None = None,
        project_path: str = ".",
    ) -> dict:
        """Add evidence to an already-documented control.

        Args:
            control_id: Control identifier (e.g., 'PR.DS-02')
            evidence_type: Type of evidence - 'config', 'code', 'document', 'url', 'screenshot', 'other'
            path: File path (relative to project) or URL
            description: Description of what this evidence demonstrates
            framework: Framework ID (default: 'nist-csf-2.0')
            line_start: Start line number (for code/config evidence)
            line_end: End line number (for code/config evidence)
            project_path: Path to project root (default: current directory)

        Returns:
            Confirmation of linked evidence.
        """
        manager = ComplianceStateManager(Path(project_path))

        line_range = None
        if line_start is not None and line_end is not None:
            line_range = (line_start, line_end)

        evidence = Evidence(
            type=EvidenceType(evidence_type),
            path=path,
            description=description,
            line_range=line_range,
        )

        await manager.link_evidence(
            framework_id=framework,
            control_id=control_id,
            evidence=evidence,
        )

        return {
            "success": True,
            "control_id": control_id,
            "evidence_type": evidence_type,
            "path": path,
            "message": f"Evidence linked to {control_id}",
        }

    @mcp.tool()
    async def get_documentation(
        framework: str = "nist-csf-2.0",
        function: str | None = None,
        category: str | None = None,
        status: str | None = None,
        include_evidence: bool = False,
        project_path: str = ".",
    ) -> dict:
        """Retrieve current compliance documentation state.

        Args:
            framework: Framework ID (default: 'nist-csf-2.0')
            function: Filter by function (e.g., 'PR')
            category: Filter by category (e.g., 'PR.DS')
            status: Filter by status
            include_evidence: Include evidence details in response
            project_path: Path to project root (default: current directory)

        Returns:
            Current compliance state with summary statistics.
        """
        manager = ComplianceStateManager(Path(project_path))

        state = await manager.get_state()
        summary = await manager.get_summary(framework_id=framework)

        # Filter controls
        controls = []
        for key, doc in state.controls.items():
            if not key.startswith(f"{framework}:"):
                continue
            if function and not doc.control_id.startswith(function):
                continue
            if category and not doc.control_id.startswith(category):
                continue
            if status and doc.status.value != status:
                continue

            control_dict = doc.model_dump()
            if not include_evidence:
                control_dict.pop("evidence", None)
            controls.append(control_dict)

        return {
            "framework": framework,
            "summary": summary.model_dump() if summary else None,
            "controls": controls,
            "generated_at": state.updated_at.isoformat(),
        }

    @mcp.tool()
    async def export_documentation(
        format: str = "markdown",
        framework: str = "nist-csf-2.0",
        include_evidence: bool = True,
        include_gaps: bool = True,
        output_path: str | None = None,
        project_path: str = ".",
    ) -> dict:
        """Export compliance documentation in various formats.

        Args:
            format: Output format - 'markdown' or 'json'
            framework: Framework ID (default: 'nist-csf-2.0')
            include_evidence: Include evidence details
            include_gaps: Include gap analysis
            output_path: Where to write the file (optional - returns content if not specified)
            project_path: Path to project root (default: current directory)

        Returns:
            Exported documentation content or file path.
        """
        manager = ComplianceStateManager(Path(project_path))

        content = await manager.export(
            format=format,
            framework_id=framework,
            include_evidence=include_evidence,
            include_gaps=include_gaps,
        )

        result = {
            "format": format,
            "framework": framework,
        }

        if output_path:
            output_file = Path(project_path) / output_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(content)
            result["output_path"] = str(output_file)
            result["message"] = f"Documentation exported to {output_path}"
        else:
            result["content"] = content

        return result
