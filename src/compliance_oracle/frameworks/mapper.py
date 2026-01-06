"""Framework mapper for cross-framework control mappings and gap analysis."""

import json
from pathlib import Path
from typing import Any

from compliance_oracle.documentation.state import ComplianceStateManager
from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import (
    ControlMapping,
    ControlStatus,
    GapAnalysisResult,
)


class FrameworkMapper:
    """Maps controls across different compliance frameworks.

    Uses NIST-provided mappings and informative references to establish
    relationships between controls in different frameworks.
    """

    def __init__(
        self,
        framework_manager: FrameworkManager | None = None,
        mappings_dir: Path | None = None,
    ) -> None:
        """Initialize the framework mapper.

        Args:
            framework_manager: Optional FrameworkManager instance.
            mappings_dir: Directory containing mapping files.
                          Defaults to data/mappings/ relative to package.
        """
        self._framework_manager = framework_manager or FrameworkManager()

        if mappings_dir is None:
            self._mappings_dir = Path(__file__).parent.parent.parent.parent / "data" / "mappings"
        else:
            self._mappings_dir = mappings_dir

        self._mappings_cache: dict[str, list[ControlMapping]] = {}

    async def _load_mappings(
        self,
        source_framework: str,
        target_framework: str,
    ) -> list[ControlMapping]:
        """Load mappings between two frameworks.

        Args:
            source_framework: Source framework ID.
            target_framework: Target framework ID.

        Returns:
            List of control mappings.
        """
        cache_key = f"{source_framework}:{target_framework}"
        if cache_key in self._mappings_cache:
            return self._mappings_cache[cache_key]

        mappings = []

        # Try to load explicit mapping file
        mapping_file = self._mappings_dir / f"{source_framework}_to_{target_framework}.json"
        if mapping_file.exists():
            with open(mapping_file) as f:
                data = json.load(f)
            for m in data.get("mappings", []):
                mappings.append(
                    ControlMapping(
                        source_control_id=m["source_control_id"],
                        source_framework_id=source_framework,
                        target_control_id=m["target_control_id"],
                        target_framework_id=target_framework,
                        relationship=m.get("relationship", "related"),
                    )
                )
        else:
            # Generate mappings from informative references
            mappings = await self._generate_mappings_from_references(
                source_framework, target_framework
            )

        self._mappings_cache[cache_key] = mappings
        return mappings

    async def _generate_mappings_from_references(
        self,
        source_framework: str,
        target_framework: str,
    ) -> list[ControlMapping]:
        """Generate mappings by analyzing informative references.

        CSF 2.0 controls have informative references that mention 800-53 controls.
        """
        mappings = []

        # Get all controls from source framework
        source_controls = await self._framework_manager.list_controls(source_framework)

        for ctrl in source_controls:
            # Get full details including informative references
            details = await self._framework_manager.get_control_details(source_framework, ctrl.id)

            if not details:
                continue

            # Parse informative references for target framework mentions
            for ref in details.informative_references:
                target_ids = self._extract_control_ids(ref, target_framework)
                for target_id in target_ids:
                    mappings.append(
                        ControlMapping(
                            source_control_id=ctrl.id,
                            source_framework_id=source_framework,
                            target_control_id=target_id,
                            target_framework_id=target_framework,
                            relationship="related",
                        )
                    )

        return mappings

    def _extract_control_ids(self, reference: str, target_framework: str) -> list[str]:
        """Extract control IDs from an informative reference string.

        Args:
            reference: Reference string (e.g., "NIST SP 800-53 Rev. 5: AC-1, AC-2")
            target_framework: Target framework to look for.

        Returns:
            List of extracted control IDs.
        """
        ids = []

        # Check if reference mentions the target framework
        if target_framework == "nist-800-53-r5":
            if "800-53" not in reference and "SP 800-53" not in reference:
                return ids

            # Pattern: control IDs are typically like "AC-1", "SC-28", etc.
            import re

            # Match patterns like AC-1, SC-28, AC-1(1), etc.
            pattern = r"\b([A-Z]{2})-(\d+)(?:\((\d+)\))?\b"
            matches = re.findall(pattern, reference)

            for match in matches:
                family, number, enhancement = match
                if enhancement:
                    ids.append(f"{family}-{number}({enhancement})")
                else:
                    ids.append(f"{family}-{number}")

        return ids

    async def get_mappings(
        self,
        control_id: str,
        source_framework: str,
        target_framework: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get mappings for a specific control.

        Args:
            control_id: Source control identifier.
            source_framework: Source framework ID.
            target_framework: Target framework ID (optional - returns all if None).

        Returns:
            List of mapping dictionaries.
        """
        results = []

        # If no target specified, get mappings to all known frameworks
        if target_framework is None:
            target_frameworks = (
                ["nist-800-53-r5"] if source_framework == "nist-csf-2.0" else ["nist-csf-2.0"]
            )
        else:
            target_frameworks = [target_framework]

        for target in target_frameworks:
            mappings = await self._load_mappings(source_framework, target)

            for mapping in mappings:
                if mapping.source_control_id == control_id:
                    results.append(
                        {
                            "target_framework": mapping.target_framework_id,
                            "target_control_id": mapping.target_control_id,
                            "relationship": mapping.relationship,
                        }
                    )

        return results

    async def analyze_gap(
        self,
        current_framework: str,
        target_framework: str,
        use_documented_state: bool = True,
        project_path: str = ".",
    ) -> GapAnalysisResult:
        """Analyze gaps between current compliance and target framework.

        Args:
            current_framework: Framework you're currently compliant with.
            target_framework: Framework you want to achieve.
            use_documented_state: Use documented compliance state vs assuming full compliance.
            project_path: Path to project for state file.

        Returns:
            Gap analysis result.
        """
        # Get all mappings from current to target
        mappings = await self._load_mappings(current_framework, target_framework)

        # Get all controls in target framework
        target_controls = await self._framework_manager.list_controls(target_framework)

        # Get current compliance state if applicable
        current_implemented: set[str] = set()
        if use_documented_state:
            state_manager = ComplianceStateManager(Path(project_path))
            state = await state_manager.get_state()

            prefix = f"{current_framework}:"
            for key, doc in state.controls.items():
                if key.startswith(prefix):
                    if doc.status in (ControlStatus.IMPLEMENTED, ControlStatus.NOT_APPLICABLE):
                        current_implemented.add(doc.control_id)
        else:
            # Assume full compliance with current framework
            current_controls = await self._framework_manager.list_controls(current_framework)
            current_implemented = {c.id for c in current_controls}

        # Build mapping from target control to source controls
        target_to_source: dict[str, list[str]] = {}
        for mapping in mappings:
            if mapping.target_control_id not in target_to_source:
                target_to_source[mapping.target_control_id] = []
            target_to_source[mapping.target_control_id].append(mapping.source_control_id)

        # Categorize target controls
        already_covered = []
        partially_covered = []
        gaps = []

        for target_ctrl in target_controls:
            source_controls = target_to_source.get(target_ctrl.id, [])

            if not source_controls:
                # No mapping - this is a gap
                gaps.append(
                    {
                        "control_id": target_ctrl.id,
                        "control_name": target_ctrl.name,
                        "description": target_ctrl.description,
                        "reason": "No mapping from current framework",
                    }
                )
            else:
                # Check how many source controls are implemented
                implemented_sources = [s for s in source_controls if s in current_implemented]

                if len(implemented_sources) == len(source_controls):
                    # All source controls implemented - fully covered
                    already_covered.append(
                        {
                            "control_id": target_ctrl.id,
                            "control_name": target_ctrl.name,
                            "covered_by": implemented_sources,
                        }
                    )
                elif implemented_sources:
                    # Some source controls implemented - partially covered
                    partially_covered.append(
                        {
                            "control_id": target_ctrl.id,
                            "control_name": target_ctrl.name,
                            "covered_by": implemented_sources,
                            "missing_coverage": [
                                s for s in source_controls if s not in current_implemented
                            ],
                        }
                    )
                else:
                    # No source controls implemented - gap despite mapping
                    gaps.append(
                        {
                            "control_id": target_ctrl.id,
                            "control_name": target_ctrl.name,
                            "description": target_ctrl.description,
                            "reason": f"Mapped controls not implemented: {source_controls}",
                        }
                    )

        return GapAnalysisResult(
            current_framework=current_framework,
            target_framework=target_framework,
            already_covered=already_covered,
            partially_covered=partially_covered,
            gaps=gaps,
            summary={
                "total_target_controls": len(target_controls),
                "fully_covered": len(already_covered),
                "partially_covered": len(partially_covered),
                "gaps": len(gaps),
                "coverage_percentage": round(
                    (len(already_covered) + len(partially_covered) * 0.5)
                    / len(target_controls)
                    * 100
                    if target_controls
                    else 0,
                    1,
                ),
            },
        )

    async def get_reverse_mappings(
        self,
        control_id: str,
        target_framework: str,
    ) -> list[dict[str, Any]]:
        """Get controls from other frameworks that map TO this control.

        Args:
            control_id: Target control identifier.
            target_framework: Framework of the target control.

        Returns:
            List of source controls that map to this control.
        """
        results = []

        # Check mappings from known frameworks
        source_frameworks = ["nist-csf-2.0", "nist-800-53-r5"]
        source_frameworks = [f for f in source_frameworks if f != target_framework]

        for source in source_frameworks:
            mappings = await self._load_mappings(source, target_framework)

            for mapping in mappings:
                if mapping.target_control_id == control_id:
                    results.append(
                        {
                            "source_framework": mapping.source_framework_id,
                            "source_control_id": mapping.source_control_id,
                            "relationship": mapping.relationship,
                        }
                    )

        return results
