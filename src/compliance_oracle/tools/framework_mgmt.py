"""Framework management tools - gap analysis, cross-framework comparison, and framework lifecycle."""

from pathlib import Path
from typing import Any

import httpx
from fastmcp import FastMCP

from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.frameworks.mapper import FrameworkMapper
from compliance_oracle.models.schemas import GapAnalysisResult
from compliance_oracle.rag.search import ControlSearcher


def register_framework_tools(mcp: FastMCP) -> None:
    """Register framework management tools with the MCP server."""

    @mcp.tool()
    async def compare_frameworks(
        control_id: str,
        source_framework: str = "nist-csf-2.0",
        target_framework: str | None = None,
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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

    @mcp.tool()
    async def manage_framework(
        action: str,
        framework: str | None = None,
        source: str | None = None,
    ) -> dict[str, Any]:
        """Manage compliance frameworks - download, update, validate, or list.

        Args:
            action: Action to perform:
                - 'list': List installed and available frameworks
                - 'download': Download framework data from official source
                - 'update': Update existing framework data
                - 'remove': Remove installed framework
                - 'validate': Validate framework data integrity
            framework: Framework ID (e.g., 'nist-csf-2.0', 'nist-800-53-r5')
                      Required for download, update, remove, validate actions
            source: Source URL or 'official' for built-in sources (for download action)

        Returns:
            Dictionary with action result, status, and message.
        """
        manager = FrameworkManager()

        if action == "list":
            return await _list_frameworks(manager)
        elif action == "download":
            if not framework:
                return {
                    "action": "download",
                    "status": "error",
                    "message": "framework parameter required for download action",
                }
            return await _download_framework(framework, source)
        elif action == "update":
            if not framework:
                return {
                    "action": "update",
                    "status": "error",
                    "message": "framework parameter required for update action",
                }
            return await _update_framework(framework, source)
        elif action == "remove":
            if not framework:
                return {
                    "action": "remove",
                    "status": "error",
                    "message": "framework parameter required for remove action",
                }
            return await _remove_framework(framework, manager)
        elif action == "validate":
            if not framework:
                return {
                    "action": "validate",
                    "status": "error",
                    "message": "framework parameter required for validate action",
                }
            return await _validate_framework(framework, manager)
        else:
            return {
                "action": action,
                "status": "error",
                "message": f"Unknown action: {action}. Valid actions: list, download, update, remove, validate",
            }


# Helper functions for manage_framework tool


async def _list_frameworks(manager: FrameworkManager) -> dict[str, Any]:
    """List installed and available frameworks."""
    frameworks = await manager.list_frameworks()

    installed = []
    available = []

    for fw in frameworks:
        fw_info = {
            "id": fw.id,
            "name": fw.name,
            "version": fw.version,
            "controls": fw.control_count,
            "status": fw.status.value,
        }

        if fw.status.value == "active":
            installed.append(fw_info)
        else:
            available.append(fw_info)

    return {
        "action": "list",
        "status": "success",
        "installed_frameworks": installed,
        "available_frameworks": available,
        "total_installed": len(installed),
        "total_available": len(available),
    }


async def _download_framework(framework: str, source: str | None = None) -> dict[str, Any]:
    """Download framework data from official source."""
    # Official NIST CPRT endpoints
    endpoints = {
        "nist-csf-2.0": "https://csrc.nist.gov/extensions/nudp/services/json/nudp/framework/version/csf_2_0_0/export/json?element=all",
        "nist-800-53-r5": "https://csrc.nist.gov/extensions/nudp/services/json/nudp/framework/version/sp_800_53_5_1_1/export/json?element=all",
        "nist-800-171-r2": "https://csrc.nist.gov/extensions/nudp/services/json/nudp/framework/version/sp_800_171_2_0_0/export/json?element=all",
    }

    if framework not in endpoints:
        return {
            "action": "download",
            "framework": framework,
            "status": "error",
            "message": f"Framework {framework} not available. Supported: {', '.join(endpoints.keys())}",
        }

    url = source if source and source != "official" else endpoints[framework]

    try:
        data_dir = Path(__file__).parent.parent.parent.parent / "data" / "frameworks"
        data_dir.mkdir(parents=True, exist_ok=True)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            output_file = data_dir / f"{framework}.json"
            output_file.write_text(response.text)

        return {
            "action": "download",
            "framework": framework,
            "status": "success",
            "message": f"Framework {framework} downloaded successfully",
            "path": str(output_file),
        }
    except httpx.HTTPError as e:
        return {
            "action": "download",
            "framework": framework,
            "status": "error",
            "message": f"Failed to download {framework}: {str(e)}",
        }
    except Exception as e:
        return {
            "action": "download",
            "framework": framework,
            "status": "error",
            "message": f"Unexpected error downloading {framework}: {str(e)}",
        }


async def _update_framework(framework: str, source: str | None = None) -> dict[str, Any]:
    """Update framework data (re-download from source)."""
    # For now, update is the same as download (overwrites existing)
    result = await _download_framework(framework, source)
    result["action"] = "update"
    if result["status"] == "success":
        result["message"] = f"Framework {framework} updated successfully"
    return result


async def _remove_framework(framework: str, manager: FrameworkManager) -> dict[str, Any]:
    """Remove installed framework data."""
    try:
        data_dir = Path(__file__).parent.parent.parent.parent / "data" / "frameworks"
        framework_file = data_dir / f"{framework}.json"

        if not framework_file.exists():
            return {
                "action": "remove",
                "framework": framework,
                "status": "error",
                "message": f"Framework {framework} not installed",
            }

        framework_file.unlink()

        # Also clear from vector store if indexed
        searcher = ControlSearcher()
        await searcher.clear_index(framework)

        return {
            "action": "remove",
            "framework": framework,
            "status": "success",
            "message": f"Framework {framework} removed successfully",
        }
    except Exception as e:
        return {
            "action": "remove",
            "framework": framework,
            "status": "error",
            "message": f"Failed to remove {framework}: {str(e)}",
        }


async def _validate_framework(framework: str, manager: FrameworkManager) -> dict[str, Any]:
    """Validate framework data integrity."""
    try:
        data_dir = Path(__file__).parent.parent.parent.parent / "data" / "frameworks"
        framework_file = data_dir / f"{framework}.json"

        if not framework_file.exists():
            return {
                "action": "validate",
                "framework": framework,
                "status": "error",
                "message": f"Framework {framework} not found",
            }

        # Try to load and parse the framework data
        import json
        with open(framework_file) as f:
            data = json.load(f)

        # Count controls
        control_count = manager._count_controls(data)

        if control_count == 0:
            return {
                "action": "validate",
                "framework": framework,
                "status": "warning",
                "message": f"Framework {framework} loaded but contains no controls",
                "control_count": 0,
            }

        return {
            "action": "validate",
            "framework": framework,
            "status": "success",
            "message": f"Framework {framework} is valid",
            "control_count": control_count,
        }
    except json.JSONDecodeError as e:
        return {
            "action": "validate",
            "framework": framework,
            "status": "error",
            "message": f"Framework {framework} has invalid JSON: {str(e)}",
        }
    except Exception as e:
        return {
            "action": "validate",
            "framework": framework,
            "status": "error",
            "message": f"Failed to validate {framework}: {str(e)}",
        }
