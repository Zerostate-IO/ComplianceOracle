"""Compliance state manager for persisting documentation state."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import (
    ComplianceState,
    ComplianceSummary,
    ControlDocumentation,
    ControlStatus,
    Evidence,
)


class ComplianceStateManager:
    """Manages compliance documentation state for a project.

    State is stored in .compliance-oracle/state.json within the project directory.
    This allows each project to have its own compliance state.
    """

    STATE_DIR = ".compliance-oracle"
    STATE_FILE = "state.json"

    def __init__(
        self,
        project_path: Path,
        framework_manager: FrameworkManager | None = None,
    ) -> None:
        """Initialize the state manager.

        Args:
            project_path: Path to the project root directory.
            framework_manager: Optional FrameworkManager instance.
        """
        self._project_path = project_path
        self._state_dir = project_path / self.STATE_DIR
        self._state_file = self._state_dir / self.STATE_FILE
        self._framework_manager = framework_manager or FrameworkManager()
        self._state: ComplianceState | None = None

    def _ensure_state_dir(self) -> None:
        """Ensure the state directory exists."""
        self._state_dir.mkdir(parents=True, exist_ok=True)

    async def _load_state(self) -> ComplianceState:
        """Load state from disk or create new state."""
        if self._state is not None:
            return self._state

        if self._state_file.exists():
            with open(self._state_file) as f:
                data = json.load(f)
            self._state = ComplianceState.model_validate(data)
        else:
            self._state = ComplianceState()

        return self._state

    async def _save_state(self) -> None:
        """Save state to disk."""
        if self._state is None:
            return

        self._ensure_state_dir()
        self._state.updated_at = datetime.utcnow()

        with open(self._state_file, "w") as f:
            json.dump(self._state.model_dump(mode="json"), f, indent=2, default=str)

    async def get_state(self) -> ComplianceState:
        """Get the current compliance state.

        Returns:
            Current compliance state.
        """
        return await self._load_state()

    async def document_control(self, doc: ControlDocumentation) -> None:
        """Document a control's compliance status.

        Args:
            doc: Control documentation to save.
        """
        state = await self._load_state()

        # Key format: framework_id:control_id
        key = f"{doc.framework_id}:{doc.control_id}"

        # If updating existing doc, preserve evidence unless explicitly cleared
        if key in state.controls and doc.evidence == []:
            existing = state.controls[key]
            doc.evidence = existing.evidence

        doc.last_updated = datetime.utcnow()
        state.controls[key] = doc

        await self._save_state()

    async def link_evidence(
        self,
        framework_id: str,
        control_id: str,
        evidence: Evidence,
    ) -> None:
        """Link evidence to a documented control.

        Args:
            framework_id: Framework identifier.
            control_id: Control identifier.
            evidence: Evidence to link.

        Raises:
            ValueError: If control is not documented.
        """
        state = await self._load_state()
        key = f"{framework_id}:{control_id}"

        if key not in state.controls:
            raise ValueError(
                f"Control {control_id} is not documented. Use document_compliance first."
            )

        doc = state.controls[key]
        doc.evidence.append(evidence)
        doc.last_updated = datetime.utcnow()

        await self._save_state()

    async def get_control_documentation(
        self,
        framework_id: str,
        control_id: str,
    ) -> ControlDocumentation | None:
        """Get documentation for a specific control.

        Args:
            framework_id: Framework identifier.
            control_id: Control identifier.

        Returns:
            Control documentation or None if not documented.
        """
        state = await self._load_state()
        key = f"{framework_id}:{control_id}"
        return state.controls.get(key)

    async def get_summary(self, framework_id: str) -> ComplianceSummary | None:
        """Get compliance summary statistics for a framework.

        Args:
            framework_id: Framework identifier.

        Returns:
            Compliance summary or None if no controls documented.
        """
        state = await self._load_state()

        # Get total controls in framework
        all_controls = await self._framework_manager.list_controls(framework_id)
        total_controls = len(all_controls)

        if total_controls == 0:
            return None

        # Count by status
        counts = {
            ControlStatus.IMPLEMENTED: 0,
            ControlStatus.PARTIAL: 0,
            ControlStatus.PLANNED: 0,
            ControlStatus.NOT_APPLICABLE: 0,
            ControlStatus.NOT_ADDRESSED: 0,
        }

        prefix = f"{framework_id}:"
        for key, doc in state.controls.items():
            if key.startswith(prefix):
                counts[doc.status] = counts.get(doc.status, 0) + 1

        # Calculate completion percentage
        # Implemented = 100%, Partial = 50%, N/A = excluded from calculation
        applicable_controls = total_controls - counts[ControlStatus.NOT_APPLICABLE]
        if applicable_controls > 0:
            completion = (
                counts[ControlStatus.IMPLEMENTED] * 100.0 + counts[ControlStatus.PARTIAL] * 50.0
            ) / applicable_controls
        else:
            completion = 100.0

        return ComplianceSummary(
            framework_id=framework_id,
            total_controls=total_controls,
            implemented=counts[ControlStatus.IMPLEMENTED],
            partial=counts[ControlStatus.PARTIAL],
            planned=counts[ControlStatus.PLANNED],
            not_applicable=counts[ControlStatus.NOT_APPLICABLE],
            not_addressed=total_controls - sum(counts.values()),
            completion_percentage=min(100.0, completion),
        )

    async def export(
        self,
        format: str,
        framework_id: str,
        include_evidence: bool = True,
        include_gaps: bool = True,
    ) -> str:
        """Export compliance documentation.

        Args:
            format: Output format ('markdown' or 'json').
            framework_id: Framework to export.
            include_evidence: Include evidence details.
            include_gaps: Include gap analysis.

        Returns:
            Formatted documentation string.
        """
        state = await self._load_state()
        summary = await self.get_summary(framework_id)

        if format == "json":
            return await self._export_json(
                state, framework_id, summary, include_evidence, include_gaps
            )
        else:
            return await self._export_markdown(
                state, framework_id, summary, include_evidence, include_gaps
            )

    async def _export_json(
        self,
        state: ComplianceState,
        framework_id: str,
        summary: ComplianceSummary | None,
        include_evidence: bool,
        include_gaps: bool,
    ) -> str:
        """Export as JSON."""
        export_data: dict[str, Any] = {
            "export_date": datetime.utcnow().isoformat(),
            "framework_id": framework_id,
            "summary": summary.model_dump() if summary else None,
            "controls": [],
        }

        prefix = f"{framework_id}:"
        for key, doc in state.controls.items():
            if key.startswith(prefix):
                control_data = doc.model_dump(mode="json")
                if not include_evidence:
                    control_data.pop("evidence", None)
                export_data["controls"].append(control_data)

        if include_gaps:
            export_data["gaps"] = await self._get_gaps(framework_id, state)

        return json.dumps(export_data, indent=2, default=str)

    async def _export_markdown(
        self,
        state: ComplianceState,
        framework_id: str,
        summary: ComplianceSummary | None,
        include_evidence: bool,
        include_gaps: bool,
    ) -> str:
        """Export as Markdown."""
        lines = [
            f"# Compliance Documentation: {framework_id}",
            "",
            f"*Generated: {datetime.utcnow().isoformat()}*",
            "",
        ]

        # Summary section
        if summary:
            lines.extend(
                [
                    "## Summary",
                    "",
                    f"- **Total Controls**: {summary.total_controls}",
                    f"- **Implemented**: {summary.implemented}",
                    f"- **Partial**: {summary.partial}",
                    f"- **Planned**: {summary.planned}",
                    f"- **Not Applicable**: {summary.not_applicable}",
                    f"- **Not Addressed**: {summary.not_addressed}",
                    f"- **Completion**: {summary.completion_percentage:.1f}%",
                    "",
                ]
            )

        # Controls by status
        lines.extend(["## Documented Controls", ""])

        prefix = f"{framework_id}:"
        docs_by_status: dict[str, list[ControlDocumentation]] = {}

        for key, doc in state.controls.items():
            if key.startswith(prefix):
                status = doc.status.value
                if status not in docs_by_status:
                    docs_by_status[status] = []
                docs_by_status[status].append(doc)

        status_order = ["implemented", "partial", "planned", "not_applicable", "not_addressed"]

        for status in status_order:
            if status in docs_by_status:
                lines.extend(
                    [
                        f"### {status.replace('_', ' ').title()}",
                        "",
                    ]
                )

                for doc in docs_by_status[status]:
                    lines.extend(
                        [
                            f"#### {doc.control_id}",
                            "",
                        ]
                    )

                    if doc.implementation_summary:
                        lines.extend(
                            [
                                doc.implementation_summary,
                                "",
                            ]
                        )

                    if doc.owner:
                        lines.append(f"**Owner**: {doc.owner}")

                    if doc.notes:
                        lines.extend(
                            [
                                "",
                                f"*Notes: {doc.notes}*",
                            ]
                        )

                    if include_evidence and doc.evidence:
                        lines.extend(
                            [
                                "",
                                "**Evidence**:",
                                "",
                            ]
                        )
                        for ev in doc.evidence:
                            line_info = ""
                            if ev.line_range:
                                line_info = f" (lines {ev.line_range[0]}-{ev.line_range[1]})"
                            lines.append(
                                f"- [{ev.type.value}] `{ev.path}`{line_info}: {ev.description}"
                            )

                    lines.append("")

        # Gaps section
        if include_gaps:
            gaps = await self._get_gaps(framework_id, state)
            if gaps:
                lines.extend(
                    [
                        "## Gaps (Not Addressed)",
                        "",
                    ]
                )
                for gap in gaps:
                    lines.append(f"- **{gap['id']}**: {gap['name']}")
                lines.append("")

        return "\n".join(lines)

    async def _get_gaps(
        self,
        framework_id: str,
        state: ComplianceState,
    ) -> list[dict[str, str]]:
        """Get list of controls not yet documented."""
        all_controls = await self._framework_manager.list_controls(framework_id)

        documented_ids = set()
        prefix = f"{framework_id}:"
        for key in state.controls:
            if key.startswith(prefix):
                control_id = key[len(prefix) :]
                documented_ids.add(control_id)

        gaps = []
        for ctrl in all_controls:
            if ctrl.id not in documented_ids:
                gaps.append(
                    {
                        "id": ctrl.id,
                        "name": ctrl.name,
                        "function": ctrl.function_name,
                        "category": ctrl.category_name,
                    }
                )

        return gaps

    async def clear_state(self) -> None:
        """Clear all compliance state."""
        self._state = ComplianceState()
        await self._save_state()

    async def remove_control(self, framework_id: str, control_id: str) -> bool:
        """Remove documentation for a control.

        Args:
            framework_id: Framework identifier.
            control_id: Control identifier.

        Returns:
            True if control was removed, False if not found.
        """
        state = await self._load_state()
        key = f"{framework_id}:{control_id}"

        if key in state.controls:
            del state.controls[key]
            await self._save_state()
            return True

        return False
