"""Framework manager for loading and querying compliance framework data."""

import json
from pathlib import Path
from typing import Any

from compliance_oracle.models.schemas import (
    Control,
    ControlDetails,
    FrameworkCategory,
    FrameworkFunction,
    FrameworkInfo,
    FrameworkStatus,
)


class FrameworkManager:
    """Manages loading and querying compliance framework data from JSON files.

    Framework data is stored in data/frameworks/ as JSON files following
    the NIST CPRT format.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        """Initialize the framework manager.

        Args:
            data_dir: Directory containing framework JSON files.
                      Defaults to data/frameworks/ relative to package.
        """
        if data_dir is None:
            # Default to data/frameworks/ relative to project root
            self._data_dir = Path(__file__).parent.parent.parent.parent / "data" / "frameworks"
        else:
            self._data_dir = data_dir

        self._cache: dict[str, dict[str, Any]] = {}
        self._framework_metadata: dict[str, FrameworkInfo] = {}

    def _get_data_dir(self) -> Path:
        """Get the data directory path."""
        return self._data_dir

    async def _load_framework(self, framework_id: str) -> dict[str, Any] | None:
        """Load framework data from JSON file.

        Args:
            framework_id: Framework identifier (e.g., 'nist-csf-2.0')

        Returns:
            Parsed framework data or None if not found.
        """
        if framework_id in self._cache:
            return self._cache[framework_id]

        # Map framework IDs to file names
        file_map = {
            "nist-csf-2.0": "nist-csf-2.0.json",
            "nist-800-53-r5": "nist-800-53-r5.json",
        }

        filename = file_map.get(framework_id)
        if not filename:
            return None

        filepath = self._data_dir / filename
        if not filepath.exists():
            return None

        with open(filepath) as f:
            data = json.load(f)

        self._cache[framework_id] = data
        return data

    async def list_frameworks(self) -> list[FrameworkInfo]:
        """List all available compliance frameworks.

        Returns:
            List of framework info objects.
        """
        frameworks = []

        # Check for known framework files
        known_frameworks = [
            {
                "id": "nist-csf-2.0",
                "name": "NIST Cybersecurity Framework 2.0",
                "version": "2.0",
                "description": "A voluntary framework for managing cybersecurity risk",
                "source_url": "https://www.nist.gov/cyberframework",
            },
            {
                "id": "nist-800-53-r5",
                "name": "NIST SP 800-53 Rev. 5",
                "version": "5.0",
                "description": "Security and Privacy Controls for Information Systems and Organizations",
                "source_url": "https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final",
            },
        ]

        for fw in known_frameworks:
            filepath = self._data_dir / f"{fw['id']}.json"
            if filepath.exists():
                # Load to get control count
                data = await self._load_framework(fw["id"])
                control_count = 0
                if data:
                    control_count = self._count_controls(data)

                frameworks.append(
                    FrameworkInfo(
                        id=fw["id"],
                        name=fw["name"],
                        version=fw["version"],
                        status=FrameworkStatus.ACTIVE,
                        description=fw["description"],
                        source_url=fw["source_url"],
                        control_count=control_count,
                    )
                )
            else:
                # Framework not installed
                frameworks.append(
                    FrameworkInfo(
                        id=fw["id"],
                        name=fw["name"],
                        version=fw["version"],
                        status=FrameworkStatus.PLANNED,
                        description=fw["description"],
                        source_url=fw["source_url"],
                        control_count=0,
                    )
                )

        return frameworks

    def _count_controls(self, data: dict[str, Any]) -> int:
        if "response" in data and "elements" in data["response"]:
            raw_elements = data["response"]["elements"].get("elements", [])
            return len(
                [e for e in raw_elements if e.get("element_type") in ["subcategory", "control"]]
            )

        if "subcategories" in data:
            return len(data.get("subcategories", []))

        if "controls" in data:
            return len(data.get("controls", []))

        count = 0
        for func in data.get("functions", []):
            for cat in func.get("categories", []):
                count += len(cat.get("subcategories", []))
        return count

    async def list_controls(
        self,
        framework_id: str,
        function_id: str | None = None,
        category_id: str | None = None,
    ) -> list[Control]:
        """List controls in a framework with optional filtering.

        Args:
            framework_id: Framework identifier
            function_id: Filter by function (e.g., 'PR', 'DE')
            category_id: Filter by category (e.g., 'PR.AC', 'DE.CM')

        Returns:
            List of controls matching the filters.
        """
        data = await self._load_framework(framework_id)
        if not data:
            return []

        controls = self._extract_controls(data, framework_id)

        # Apply filters
        if function_id:
            controls = [c for c in controls if c.function_id == function_id]
        if category_id:
            controls = [c for c in controls if c.category_id == category_id]

        return controls

    def _extract_controls(self, data: dict[str, Any], framework_id: str) -> list[Control]:
        controls = []

        if "response" in data and "elements" in data["response"]:
            elements_data = data["response"]["elements"]
            raw_elements = elements_data.get("elements", [])

            if framework_id == "nist-csf-2.0":
                functions = {
                    e["element_identifier"]: e
                    for e in raw_elements
                    if e.get("element_type") == "function"
                }
                categories = {
                    e["element_identifier"]: e
                    for e in raw_elements
                    if e.get("element_type") == "category"
                }

                for e in raw_elements:
                    if e.get("element_type") == "subcategory":
                        sub_id = e.get("element_identifier", "")
                        cat_id = ".".join(sub_id.split(".")[:2]) if "." in sub_id else ""
                        cat = categories.get(cat_id, {})
                        func_id = cat_id.split(".")[0] if "." in cat_id else ""
                        func = functions.get(func_id, {})

                        controls.append(
                            Control(
                                id=sub_id,
                                name=e.get("title", sub_id) or sub_id,
                                description=e.get("text", ""),
                                framework_id=framework_id,
                                function_id=func_id,
                                function_name=func.get("title", func_id),
                                category_id=cat_id,
                                category_name=cat.get("title", cat_id),
                                implementation_examples=e.get("implementation_examples", []),
                                informative_references=e.get("informative_references", []),
                                keywords=e.get("keywords", []),
                            )
                        )
            elif framework_id == "nist-800-53-r5":
                families = {
                    e["element_identifier"]: e
                    for e in raw_elements
                    if e.get("element_type") == "family"
                }
                for e in raw_elements:
                    if e.get("element_type") == "control":
                        ctrl_id = e.get("element_identifier", "")
                        family_id = ctrl_id.split("-")[0] if "-" in ctrl_id else ""
                        family = families.get(family_id, {})

                        controls.append(
                            Control(
                                id=ctrl_id,
                                name=e.get("title", ctrl_id) or ctrl_id,
                                description=e.get("text", ""),
                                framework_id=framework_id,
                                function_id=family_id,
                                function_name=family.get("title", family_id),
                                category_id=family_id,
                                category_name=family.get("title", family_id),
                                implementation_examples=e.get("implementation_examples", []),
                                informative_references=e.get("informative_references", []),
                                keywords=e.get("keywords", []),
                            )
                        )
            return controls

        if "subcategories" in data:
            functions = {f["id"]: f for f in data.get("functions", [])}
            categories = {c["id"]: c for c in data.get("categories", [])}

            for sub in data.get("subcategories", []):
                cat_id = sub.get("category_id", "")
                cat = categories.get(cat_id, {})
                func_id = cat.get("function_id", "")
                func = functions.get(func_id, {})

                controls.append(
                    Control(
                        id=sub.get("id", ""),
                        name=sub.get("name", sub.get("id", "")),
                        description=sub.get("description", ""),
                        framework_id=framework_id,
                        function_id=func_id,
                        function_name=func.get("name", func_id),
                        category_id=cat_id,
                        category_name=cat.get("name", cat_id),
                        implementation_examples=sub.get("implementation_examples", []),
                        informative_references=sub.get("informative_references", []),
                        keywords=sub.get("keywords", []),
                    )
                )

        # NIST CSF 2.0 nested format
        elif "functions" in data:
            for func in data.get("functions", []):
                func_id = func.get("id", "")
                func_name = func.get("name", func_id)

                for cat in func.get("categories", []):
                    cat_id = cat.get("id", "")
                    cat_name = cat.get("name", cat_id)

                    for sub in cat.get("subcategories", []):
                        controls.append(
                            Control(
                                id=sub.get("id", ""),
                                name=sub.get("name", sub.get("id", "")),
                                description=sub.get("description", ""),
                                framework_id=framework_id,
                                function_id=func_id,
                                function_name=func_name,
                                category_id=cat_id,
                                category_name=cat_name,
                                implementation_examples=sub.get("implementation_examples", []),
                                informative_references=sub.get("informative_references", []),
                                keywords=sub.get("keywords", []),
                            )
                        )

        # NIST 800-53 format
        elif "controls" in data:
            for ctrl in data.get("controls", []):
                family_id = ctrl.get("family_id", "")
                family_name = ctrl.get("family_name", family_id)

                controls.append(
                    Control(
                        id=ctrl.get("id", ""),
                        name=ctrl.get("name", ctrl.get("id", "")),
                        description=ctrl.get("description", ""),
                        framework_id=framework_id,
                        function_id=family_id,  # Map family to function
                        function_name=family_name,
                        category_id=family_id,  # 800-53 doesn't have categories like CSF
                        category_name=family_name,
                        implementation_examples=ctrl.get("implementation_examples", []),
                        informative_references=ctrl.get("informative_references", []),
                        keywords=ctrl.get("keywords", []),
                    )
                )

        return controls

    async def get_control_details(
        self,
        framework_id: str,
        control_id: str,
    ) -> ControlDetails | None:
        """Get full details for a specific control.

        Args:
            framework_id: Framework identifier
            control_id: Control identifier

        Returns:
            Control details or None if not found.
        """
        data = await self._load_framework(framework_id)
        if not data:
            return None

        controls = self._extract_controls(data, framework_id)

        for ctrl in controls:
            if ctrl.id == control_id:
                # Get additional details like mappings
                mappings = await self._get_control_mappings(data, control_id)
                related = await self._get_related_controls(data, control_id)

                return ControlDetails(
                    id=ctrl.id,
                    name=ctrl.name,
                    description=ctrl.description,
                    framework_id=ctrl.framework_id,
                    function_id=ctrl.function_id,
                    function_name=ctrl.function_name,
                    category_id=ctrl.category_id,
                    category_name=ctrl.category_name,
                    implementation_examples=ctrl.implementation_examples,
                    informative_references=ctrl.informative_references,
                    keywords=ctrl.keywords,
                    related_controls=related,
                    mappings=mappings,
                )

        return None

    async def _get_control_mappings(
        self,
        data: dict[str, Any],
        control_id: str,
    ) -> dict[str, list[str]]:
        """Get cross-framework mappings for a control."""
        mappings: dict[str, list[str]] = {}

        # Look for mappings in the data
        for sub in data.get("subcategories", []):
            if sub.get("id") == control_id:
                # CSF 2.0 has informative references that may include 800-53 mappings
                for ref in sub.get("informative_references", []):
                    if "800-53" in ref or "SP 800-53" in ref:
                        if "nist-800-53-r5" not in mappings:
                            mappings["nist-800-53-r5"] = []
                        # Extract control IDs from reference
                        # Format is usually "NIST SP 800-53 Rev. 5: AC-1, AC-2"
                        mappings["nist-800-53-r5"].append(ref)

        return mappings

    async def _get_related_controls(
        self,
        data: dict[str, Any],
        control_id: str,
    ) -> list[str]:
        """Get related controls within the same framework."""
        related = []

        # Find controls in the same category
        for sub in data.get("subcategories", []):
            if sub.get("id") == control_id:
                cat_id = sub.get("category_id", "")
                # Find other controls in same category
                for other in data.get("subcategories", []):
                    other_cat = other.get("category_id", "")
                    other_id = other.get("id", "")
                    if other_cat == cat_id and other_id != control_id:
                        related.append(other_id)
                break

        return related

    async def get_functions(self, framework_id: str) -> list[FrameworkFunction]:
        """Get all functions in a framework.

        Args:
            framework_id: Framework identifier

        Returns:
            List of framework functions.
        """
        data = await self._load_framework(framework_id)
        if not data:
            return []

        functions = []
        for func in data.get("functions", []):
            functions.append(
                FrameworkFunction(
                    id=func.get("id", ""),
                    name=func.get("name", ""),
                    description=func.get("description"),
                )
            )

        return functions

    async def get_categories(
        self,
        framework_id: str,
        function_id: str | None = None,
    ) -> list[FrameworkCategory]:
        """Get categories in a framework.

        Args:
            framework_id: Framework identifier
            function_id: Filter by function (optional)

        Returns:
            List of framework categories.
        """
        data = await self._load_framework(framework_id)
        if not data:
            return []

        categories = []
        for cat in data.get("categories", []):
            if function_id and cat.get("function_id") != function_id:
                continue
            categories.append(
                FrameworkCategory(
                    id=cat.get("id", ""),
                    name=cat.get("name", ""),
                    description=cat.get("description"),
                    function_id=cat.get("function_id", ""),
                )
            )

        return categories
