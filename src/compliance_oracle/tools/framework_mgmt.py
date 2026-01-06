"""Framework management tools - gap analysis and cross-framework comparison."""

from fastmcp import FastMCP

from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.frameworks.mapper import FrameworkMapper
from compliance_oracle.models.schemas import GapAnalysisResult


def register_framework_tools(mcp: FastMCP) -> None:
    """Register framework management tools with the MCP server."""

    @mcp.tool()
    async def compare_frameworks(
        control_id: str,
        source_framework: str = "nist-csf-2.0",
        target_framework: str | None = None,
    ) -> dict:
        """Compare controls across frameworks or show mappings.

        Args:
            control_id: Control to find mappings for (e.g., 'PR.AC-03')
            source_framework: Framework of the source control
            target_framework: Framework to map to (optional - shows all if omitted)

        Returns:
            Cross-framework mappings for the control.
        """
        mapper = FrameworkMapper()

        source_control = {
            "framework": source_framework,
            "control_id": control_id,
        }

        mappings = await mapper.get_mappings(
            control_id=control_id,
            source_framework=source_framework,
            target_framework=target_framework,
        )

        return {
            "source": source_control,
            "mappings": mappings,
        }

    @mcp.tool()
    async def get_framework_gap(
        current_framework: str,
        target_framework: str,
        use_documented_state: bool = True,
        project_path: str = ".",
    ) -> GapAnalysisResult:
        """Analyze what's needed to achieve compliance with a target framework.

        Given your current compliance state with one framework, determine
        what additional work is needed for another framework.

        Args:
            current_framework: Framework you're currently compliant with
            target_framework: Framework you want to achieve
            use_documented_state: Use your documented compliance state
                                  (vs assuming full compliance)
            project_path: Path to project root for state file

        Returns:
            Gap analysis showing:
            - Controls already covered
            - Partially covered controls
            - Gaps requiring new work
            - Effort estimates
        """
        mapper = FrameworkMapper()

        return await mapper.analyze_gap(
            current_framework=current_framework,
            target_framework=target_framework,
            use_documented_state=use_documented_state,
            project_path=project_path,
        )

    @mcp.tool()
    async def get_guidance(
        control_id: str,
        framework: str = "nist-csf-2.0",
        context: str | None = None,
        detail_level: str = "detailed",
    ) -> dict:
        """Get implementation guidance for a specific control.

        Args:
            control_id: Control identifier (e.g., 'PR.AC-03')
            framework: Framework ID (default: 'nist-csf-2.0')
            context: Optional context about your environment
            detail_level: 'summary', 'detailed', or 'checklist'

        Returns:
            Implementation guidance including:
            - Overview
            - Key activities
            - Common technologies
            - Checklist items
        """
        manager = FrameworkManager()

        control = await manager.get_control_details(
            framework_id=framework,
            control_id=control_id,
        )

        if not control:
            return {
                "error": f"Control {control_id} not found in {framework}",
            }

        # Build guidance response
        guidance = {
            "control_id": control.id,
            "control_name": control.name,
            "description": control.description,
            "implementation_guidance": {
                "overview": control.description,
                "implementation_examples": control.implementation_examples,
                "informative_references": control.informative_references,
            },
            "related_controls": control.related_controls,
            "cross_framework_mappings": control.mappings,
        }

        return guidance
