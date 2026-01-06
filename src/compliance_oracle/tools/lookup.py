"""Shared lookup tools for framework and control information."""

from fastmcp import FastMCP

from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import (
    Control,
    ControlDetails,
    FrameworkInfo,
    ListControlsResponse,
    ListFrameworksResponse,
)


def register_lookup_tools(mcp: FastMCP) -> None:
    """Register lookup tools with the MCP server."""

    @mcp.tool()
    async def list_frameworks() -> ListFrameworksResponse:
        """List all available compliance frameworks.

        Returns information about installed frameworks including their ID,
        name, version, and number of controls.
        """
        manager = FrameworkManager()
        frameworks = await manager.list_frameworks()
        return ListFrameworksResponse(frameworks=frameworks)

    @mcp.tool()
    async def list_controls(
        framework: str = "nist-csf-2.0",
        function: str | None = None,
        category: str | None = None,
    ) -> ListControlsResponse:
        """Browse controls in a compliance framework.

        Args:
            framework: Framework ID (e.g., 'nist-csf-2.0', 'nist-800-53-r5')
            function: Filter by function ID (e.g., 'PR', 'DE', 'GV')
            category: Filter by category ID (e.g., 'PR.AC', 'DE.CM')

        Returns:
            List of controls matching the filters.
        """
        manager = FrameworkManager()
        controls = await manager.list_controls(
            framework_id=framework,
            function_id=function,
            category_id=category,
        )
        return ListControlsResponse(
            framework_id=framework,
            function=function,
            category=category,
            controls=controls,
            total_count=len(controls),
        )

    @mcp.tool()
    async def get_control_details(
        control_id: str,
        framework: str = "nist-csf-2.0",
    ) -> ControlDetails | None:
        """Get full details for a specific control.

        Args:
            control_id: Control identifier (e.g., 'PR.AC-01', 'GV.OC-01')
            framework: Framework ID (default: 'nist-csf-2.0')

        Returns:
            Full control details including implementation examples,
            informative references, and cross-framework mappings.
            Returns None if control not found.
        """
        manager = FrameworkManager()
        return await manager.get_control_details(
            framework_id=framework,
            control_id=control_id,
        )
