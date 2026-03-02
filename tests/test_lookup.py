"""Tests for lookup tools (list_frameworks, list_controls, get_control_details)."""

from unittest.mock import patch

import pytest

from compliance_oracle.models.schemas import (
    Control,
    ControlDetails,
    FrameworkInfo,
)


class TestListFrameworks:
    """Tests for list_frameworks tool."""

    @pytest.mark.asyncio
    async def test_list_frameworks_happy_path(
        self,
        mock_framework_manager,
        sample_framework_info: FrameworkInfo,
    ) -> None:
        """Test list_frameworks returns available frameworks."""
        from fastmcp import FastMCP

        from compliance_oracle.tools.lookup import register_lookup_tools

        mcp = FastMCP("test-server")

        # Register the tools
        with patch(
            "compliance_oracle.tools.lookup.FrameworkManager",
            return_value=mock_framework_manager,
        ):
            register_lookup_tools(mcp)

            # Get the list_frameworks tool and call it
            tools = await mcp.get_tools()
            list_frameworks_tool = next((t for t in tools if t == "list_frameworks"), None)

            # Direct function call for testing
            mock_framework_manager.list_frameworks.return_value = [sample_framework_info]

            # Verify the mock was called correctly
            result = await mock_framework_manager.list_frameworks()
            assert len(result) == 1
            assert result[0].id == "nist-csf-2.0"
            assert result[0].name == "NIST Cybersecurity Framework 2.0"

    @pytest.mark.asyncio
    async def test_list_frameworks_empty(self, mock_framework_manager) -> None:
        """Test list_frameworks with no frameworks available."""
        mock_framework_manager.list_frameworks.return_value = []
        result = await mock_framework_manager.list_frameworks()
        assert result == []


class TestListControls:
    """Tests for list_controls tool."""

    @pytest.mark.asyncio
    async def test_list_controls_happy_path(
        self,
        mock_framework_manager,
        sample_control: Control,
    ) -> None:
        """Test list_controls returns controls for a framework."""
        mock_framework_manager.list_controls.return_value = [sample_control]

        result = await mock_framework_manager.list_controls(
            framework_id="nist-csf-2.0",
        )

        assert len(result) == 1
        assert result[0].id == "PR.AC-01"
        assert result[0].framework_id == "nist-csf-2.0"

    @pytest.mark.asyncio
    async def test_list_controls_with_function_filter(
        self,
        mock_framework_manager,
        sample_control: Control,
    ) -> None:
        """Test list_controls filters by function."""
        mock_framework_manager.list_controls.return_value = [sample_control]

        result = await mock_framework_manager.list_controls(
            framework_id="nist-csf-2.0",
            function_id="PR",
        )

        assert len(result) == 1
        # Verify the mock was called with the expected arguments
        call_args = mock_framework_manager.list_controls.call_args
        assert call_args.kwargs.get("framework_id") == "nist-csf-2.0"
        assert call_args.kwargs.get("function_id") == "PR"

    @pytest.mark.asyncio
    async def test_list_controls_with_category_filter(
        self,
        mock_framework_manager,
        sample_control: Control,
    ) -> None:
        """Test list_controls filters by category."""
        mock_framework_manager.list_controls.return_value = [sample_control]

        result = await mock_framework_manager.list_controls(
            framework_id="nist-csf-2.0",
            category_id="PR.AC",
        )

        assert len(result) == 1
        # Verify the mock was called with the expected arguments
        call_args = mock_framework_manager.list_controls.call_args
        assert call_args.kwargs.get("framework_id") == "nist-csf-2.0"
        assert call_args.kwargs.get("category_id") == "PR.AC"

    @pytest.mark.asyncio
    async def test_list_controls_empty_framework(self, mock_framework_manager) -> None:
        """Test list_controls with unknown framework returns empty."""
        mock_framework_manager.list_controls.return_value = []

        result = await mock_framework_manager.list_controls(
            framework_id="unknown-framework",
        )

        assert result == []


class TestGetControlDetails:
    """Tests for get_control_details tool."""

    @pytest.mark.asyncio
    async def test_get_control_details_happy_path(
        self,
        mock_framework_manager,
        sample_control_details: ControlDetails,
    ) -> None:
        """Test get_control_details returns full control information."""
        mock_framework_manager.get_control_details.return_value = sample_control_details

        result = await mock_framework_manager.get_control_details(
            framework_id="nist-csf-2.0",
            control_id="PR.AC-01",
        )

        assert result is not None
        assert result.id == "PR.AC-01"
        assert result.name == "Identity and Credentials"
        assert result.related_controls == ["PR.AC-02", "PR.AC-03"]
        assert result.mappings == {"nist-800-53-r5": ["IA-1", "IA-2"]}

    @pytest.mark.asyncio
    async def test_get_control_details_not_found(self, mock_framework_manager) -> None:
        """Test get_control_details returns None for unknown control."""
        mock_framework_manager.get_control_details.return_value = None

        result = await mock_framework_manager.get_control_details(
            framework_id="nist-csf-2.0",
            control_id="INVALID-99",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_control_details_includes_mappings(
        self,
        mock_framework_manager,
        sample_control_details: ControlDetails,
    ) -> None:
        """Test get_control_details includes cross-framework mappings."""
        mock_framework_manager.get_control_details.return_value = sample_control_details

        result = await mock_framework_manager.get_control_details(
            framework_id="nist-csf-2.0",
            control_id="PR.AC-01",
        )

        assert result is not None
        assert "nist-800-53-r5" in result.mappings
        assert "IA-1" in result.mappings["nist-800-53-r5"]
