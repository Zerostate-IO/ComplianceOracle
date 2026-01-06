"""Framework mapper for cross-framework control mappings and gap analysis."""

import json
from pathlib import Path
from typing import Any

from compliance_oracle.documentation.state import ComplianceStateManager
from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.models.schemas import (
    ControlMapping,
    ControlRelationship,
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
                rel_str = m.get("relationship", "related")
                rel_map = {
                    "equivalent": ControlRelationship.EQUIVALENT,
                    "subset": ControlRelationship.NARROWER,
                    "narrower": ControlRelationship.NARROWER,
                    "superset": ControlRelationship.BROADER,
                    "broader": ControlRelationship.BROADER,
                    "related": ControlRelationship.RELATED,
                }
                relationship = rel_map.get(rel_str, ControlRelationship.RELATED)

                mappings.append(
                    ControlMapping(
                        source_control_id=m["source_control_id"],
                        source_framework_id=source_framework,
                        target_control_id=m["target_control_id"],
                        target_framework_id=target_framework,
                        relationship=relationship,
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
                            relationship=ControlRelationship.RELATED,
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

        This treats the current framework as the source of truth and uses
        crosswalk mappings (with relationship types) to project hypothetical
        coverage into the target framework.

        Args:
            current_framework: Framework you're currently compliant with.
            target_framework: Framework you want to achieve.
            use_documented_state: Use documented compliance state vs assuming full compliance.
            project_path: Path to project for state file.

        Returns:
            Gap analysis result, including fully covered, partially covered,
            and gap controls in the target framework.
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

        # Build mapping from target control to list of ControlMapping objects
        target_to_mappings: dict[str, list[ControlMapping]] = {}
        for mapping in mappings:
            target_to_mappings.setdefault(mapping.target_control_id, []).append(mapping)

        # Categorize target controls
        already_covered: list[dict[str, Any]] = []
        partially_covered: list[dict[str, Any]] = []
        gaps: list[dict[str, Any]] = []

        for target_ctrl in target_controls:
            mappings_for_target = target_to_mappings.get(target_ctrl.id, [])

            if not mappings_for_target:
                # No mapping - this is a gap
                gaps.append(
                    {
                        "control_id": target_ctrl.id,
                        "control_name": target_ctrl.name,
                        "description": target_ctrl.description,
                        "reason": "No mapping from current framework",
                    }
                )
                continue

            # Group mappings by relationship type
            eq = [
                m for m in mappings_for_target if m.relationship == ControlRelationship.EQUIVALENT
            ]
            broader = [
                m for m in mappings_for_target if m.relationship == ControlRelationship.BROADER
            ]
            narrower = [
                m for m in mappings_for_target if m.relationship == ControlRelationship.NARROWER
            ]
            related = [
                m for m in mappings_for_target if m.relationship == ControlRelationship.RELATED
            ]

            # Helper sets
            all_source_controls = {m.source_control_id for m in mappings_for_target}
            implemented_all = [s for s in all_source_controls if s in current_implemented]

            # First, consider equivalent/broader mappings as strongest evidence
            eq_broader = eq + broader
            if eq_broader:
                eq_broader_sources = {m.source_control_id for m in eq_broader}
                implemented_eq_broader = [s for s in eq_broader_sources if s in current_implemented]
                missing_eq_broader = [s for s in eq_broader_sources if s not in current_implemented]

                if implemented_eq_broader and not missing_eq_broader:
                    already_covered.append(
                        {
                            "control_id": target_ctrl.id,
                            "control_name": target_ctrl.name,
                            "covered_by": implemented_eq_broader,
                            "relationship_summary": "equivalent/broader mappings fully implemented",
                        }
                    )
                    continue
                elif implemented_eq_broader:
                    partially_covered.append(
                        {
                            "control_id": target_ctrl.id,
                            "control_name": target_ctrl.name,
                            "covered_by": implemented_eq_broader,
                            "missing_coverage": missing_eq_broader,
                            "relationship_summary": "some equivalent/broader mappings implemented",
                        }
                    )
                    continue

            # Next, consider narrower mappings (source is narrower than target)
            if narrower:
                narrow_sources = {m.source_control_id for m in narrower}
                implemented_narrow = [s for s in narrow_sources if s in current_implemented]
                missing_narrow = [s for s in narrow_sources if s not in current_implemented]

                if implemented_narrow:
                    partially_covered.append(
                        {
                            "control_id": target_ctrl.id,
                            "control_name": target_ctrl.name,
                            "covered_by": implemented_narrow,
                            "missing_coverage": missing_narrow,
                            "relationship_summary": "source controls are narrower than target; partial coverage inferred",
                        }
                    )
                    continue

            # If we reach here, there are no implemented equivalent/broader/narrower mappings
            if related:
                gaps.append(
                    {
                        "control_id": target_ctrl.id,
                        "control_name": target_ctrl.name,
                        "description": target_ctrl.description,
                        "reason": "Only related mappings exist; needs direct assessment in target framework",
                        "mapped_from": sorted({m.source_control_id for m in related}),
                    }
                )
            else:
                # Mapped, but none of the mapped controls are implemented
                gaps.append(
                    {
                        "control_id": target_ctrl.id,
                        "control_name": target_ctrl.name,
                        "description": target_ctrl.description,
                        "reason": f"Mapped controls not implemented: {sorted(all_source_controls)}",
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
