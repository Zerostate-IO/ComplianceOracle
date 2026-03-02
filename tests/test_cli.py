"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from click.testing import CliRunner

from compliance_oracle.cli import main


class TestExportCommand:
    """Tests for the export CLI command."""

    def test_export_markdown_happy_path(self, tmp_path: Path) -> None:
        """Test export command with markdown format."""
        from compliance_oracle.models.schemas import (
            ComplianceState,
            ControlDocumentation,
            ControlStatus,
        )

        runner = CliRunner()

        # Create a documented control
        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
            implementation_summary="Test implementation",
        )
        state = ComplianceState(controls={"nist-csf-2.0:PR.AC-01": doc})

        output_file = tmp_path / "export.md"

        with patch("compliance_oracle.cli.ComplianceStateManager") as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.export = AsyncMock(
                return_value="# Compliance Documentation\n\n## Summary\n..."
            )
            mock_manager_class.return_value = mock_instance

            result = runner.invoke(
                main,
                [
                    "export",
                    "--format",
                    "markdown",
                    "--framework",
                    "nist-csf-2.0",
                    "--output",
                    str(output_file),
                    "--project-path",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            assert output_file.exists()
            assert "# Compliance Documentation" in output_file.read_text()

    def test_export_json_happy_path(self, tmp_path: Path) -> None:
        """Test export command with JSON format."""
        from compliance_oracle.models.schemas import (
            ComplianceState,
            ControlDocumentation,
            ControlStatus,
        )

        runner = CliRunner()

        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
        )
        state = ComplianceState(controls={"nist-csf-2.0:PR.AC-01": doc})

        output_file = tmp_path / "export.json"

        with patch("compliance_oracle.cli.ComplianceStateManager") as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.export = AsyncMock(
                return_value='{"framework_id": "nist-csf-2.0", "controls": []}'
            )
            mock_manager_class.return_value = mock_instance

            result = runner.invoke(
                main,
                [
                    "export",
                    "--format",
                    "json",
                    "--framework",
                    "nist-csf-2.0",
                    "--output",
                    str(output_file),
                    "--project-path",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            assert output_file.exists()
            assert "framework_id" in output_file.read_text()

    def test_export_invalid_format_exits_with_error(self, tmp_path: Path) -> None:
        """Test export command with invalid format exits non-zero."""
        runner = CliRunner()
        output_file = tmp_path / "export.pdf"

        result = runner.invoke(
            main,
            [
                "export",
                "--format",
                "latex",  # Invalid format
                "--framework",
                "nist-csf-2.0",
                "--output",
                str(output_file),
            ],
        )

        # Click should reject invalid choice
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "latex" in result.output.lower()

    def test_export_missing_output_exits_with_error(self, tmp_path: Path) -> None:
        """Test export command without --output exits with error."""
        runner = CliRunner()

        result = runner.invoke(
            main,
            [
                "export",
                "--format",
                "json",
                "--framework",
                "nist-csf-2.0",
                # Missing --output
            ],
        )

        assert result.exit_code != 0
        assert "Missing option" in result.output or "--output" in result.output

    def test_export_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test export creates parent directories if they don't exist."""
        from compliance_oracle.models.schemas import ComplianceState

        runner = CliRunner()
        state = ComplianceState(controls={})
        output_file = tmp_path / "nested" / "dir" / "export.md"

        with patch("compliance_oracle.cli.ComplianceStateManager") as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.export = AsyncMock(return_value="# Report")
            mock_manager_class.return_value = mock_instance

            result = runner.invoke(
                main,
                [
                    "export",
                    "--format",
                    "markdown",
                    "--output",
                    str(output_file),
                    "--project-path",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            assert output_file.exists()

    def test_export_with_evidence_flag(self, tmp_path: Path) -> None:
        """Test export with --include-evidence flag."""
        from compliance_oracle.models.schemas import (
            ComplianceState,
            ControlDocumentation,
            ControlStatus,
        )

        runner = CliRunner()

        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
        )
        state = ComplianceState(controls={"nist-csf-2.0:PR.AC-01": doc})
        output_file = tmp_path / "export.md"

        with patch("compliance_oracle.cli.ComplianceStateManager") as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.export = AsyncMock(return_value="# Report with evidence")
            mock_manager_class.return_value = mock_instance

            result = runner.invoke(
                main,
                [
                    "export",
                    "--format",
                    "markdown",
                    "--output",
                    str(output_file),
                    "--include-evidence",
                    "--project-path",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            # Verify export was called with include_evidence=True
            mock_instance.export.assert_called_once()
            call_kwargs = mock_instance.export.call_args.kwargs
            assert call_kwargs["include_evidence"] is True

    def test_export_with_gaps_flag(self, tmp_path: Path) -> None:
        """Test export with --include-gaps flag."""
        from compliance_oracle.models.schemas import (
            ComplianceState,
            ControlDocumentation,
            ControlStatus,
        )

        runner = CliRunner()

        doc = ControlDocumentation(
            control_id="PR.AC-01",
            framework_id="nist-csf-2.0",
            status=ControlStatus.IMPLEMENTED,
        )
        state = ComplianceState(controls={"nist-csf-2.0:PR.AC-01": doc})
        output_file = tmp_path / "export.md"

        with patch("compliance_oracle.cli.ComplianceStateManager") as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.export = AsyncMock(return_value="# Report with gaps")
            mock_manager_class.return_value = mock_instance

            result = runner.invoke(
                main,
                [
                    "export",
                    "--format",
                    "markdown",
                    "--output",
                    str(output_file),
                    "--include-gaps",
                    "--project-path",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            # Verify export was called with include_gaps=True
            mock_instance.export.assert_called_once()
            call_kwargs = mock_instance.export.call_args.kwargs
            assert call_kwargs["include_gaps"] is True

    def test_export_no_documentation_shows_message(self, tmp_path: Path) -> None:
        """Test export with no documentation shows informative message."""
        from compliance_oracle.models.schemas import ComplianceState

        runner = CliRunner()
        state = ComplianceState(controls={})
        output_file = tmp_path / "export.md"

        with patch("compliance_oracle.cli.ComplianceStateManager") as mock_manager_class:
            mock_instance = MagicMock()
            mock_instance.get_state = AsyncMock(return_value=state)
            mock_instance.export = AsyncMock(return_value="# Empty Report")
            mock_manager_class.return_value = mock_instance

            result = runner.invoke(
                main,
                [
                    "export",
                    "--format",
                    "markdown",
                    "--output",
                    str(output_file),
                    "--project-path",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            assert "No documentation found" in result.output


class TestCliHelp:
    """Tests for CLI help and discovery."""

    def test_main_help_shows_export(self) -> None:
        """Test that export command appears in help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "export" in result.output

    def test_export_help_shows_options(self) -> None:
        """Test that export help shows all options."""
        runner = CliRunner()
        result = runner.invoke(main, ["export", "--help"])
        assert result.exit_code == 0
        assert "--format" in result.output
        assert "--framework" in result.output
        assert "--output" in result.output
        assert "--include-evidence" in result.output
        assert "--include-gaps" in result.output
