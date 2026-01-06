#!/usr/bin/env python3
"""Fetch NIST framework data from CPRT API.

This script downloads NIST CSF 2.0 and SP 800-53 Rev. 5 data from the NIST
Cybersecurity and Privacy Reference Tool (CPRT) API.

Usage:
    python scripts/fetch_nist_data.py
    python scripts/fetch_nist_data.py --framework nist-csf-2.0
    python scripts/fetch_nist_data.py --output-dir /path/to/output
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def fetch_framework(framework_id: str, output_dir: Path) -> bool:
    """Fetch framework data from NIST CPRT API.

    Args:
        framework_id: Framework identifier.
        output_dir: Directory to save the data.

    Returns:
        True if successful, False otherwise.
    """
    import httpx

    # NIST CPRT API endpoints
    endpoints = {
        "nist-csf-2.0": "https://csrc.nist.gov/extensions/nudp/services/json/csf/download?element=all",
        "nist-800-53-r5": "https://csrc.nist.gov/extensions/nudp/services/json/sp800-53/download?release=5.1.1",
    }

    url = endpoints.get(framework_id)
    if not url:
        print(f"ERROR: Unknown framework: {framework_id}", file=sys.stderr)
        return False

    print(f"Fetching {framework_id} from {url}...")

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.get(url)
            response.raise_for_status()

            data = response.json()

            # Transform data if needed
            transformed = transform_framework_data(framework_id, data)

            # Save to file
            output_file = output_dir / f"{framework_id}.json"
            with open(output_file, "w") as f:
                json.dump(transformed, f, indent=2)

            print(f"Saved to {output_file}")
            return True

    except httpx.HTTPError as e:
        print(f"ERROR: Failed to fetch {framework_id}: {e}", file=sys.stderr)
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON response for {framework_id}: {e}", file=sys.stderr)
        return False


def transform_framework_data(framework_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Transform NIST API response to our internal format.

    The NIST API returns data in various formats. This function normalizes
    it to a consistent structure.
    """
    if framework_id == "nist-csf-2.0":
        return transform_csf_data(data)
    elif framework_id == "nist-800-53-r5":
        return transform_800_53_data(data)
    return data


def transform_csf_data(data: dict[str, Any]) -> dict[str, Any]:
    """Transform NIST CSF 2.0 data to our format.

    Expected input structure varies, but we normalize to:
    {
        "framework_id": "nist-csf-2.0",
        "version": "2.0",
        "functions": [...],
        "categories": [...],
        "subcategories": [...]  # These are the actual controls
    }
    """
    result: dict[str, Any] = {
        "framework_id": "nist-csf-2.0",
        "version": "2.0",
        "functions": [],
        "categories": [],
        "subcategories": [],
    }

    # Handle different possible response structures
    if "functions" in data:
        # Already structured
        result["functions"] = data.get("functions", [])
        result["categories"] = data.get("categories", [])
        result["subcategories"] = data.get("subcategories", [])
    elif "elements" in data:
        # Elements-based structure
        functions = {}
        categories = {}
        subcategories = []

        for elem in data.get("elements", []):
            elem_type = elem.get("element_type", "").lower()

            if elem_type == "function":
                functions[elem.get("element_identifier")] = {
                    "id": elem.get("element_identifier", ""),
                    "name": elem.get("element_name", ""),
                    "description": elem.get("element_text", ""),
                }
            elif elem_type == "category":
                cat_id = elem.get("element_identifier", "")
                func_id = cat_id.split(".")[0] if "." in cat_id else ""
                categories[cat_id] = {
                    "id": cat_id,
                    "name": elem.get("element_name", ""),
                    "description": elem.get("element_text", ""),
                    "function_id": func_id,
                }
            elif elem_type == "subcategory":
                sub_id = elem.get("element_identifier", "")
                cat_id = ".".join(sub_id.split(".")[:2]) if "." in sub_id else ""
                subcategories.append(
                    {
                        "id": sub_id,
                        "name": elem.get("element_name", sub_id),
                        "description": elem.get("element_text", ""),
                        "category_id": cat_id,
                        "implementation_examples": elem.get("implementation_examples", []),
                        "informative_references": elem.get("informative_references", []),
                    }
                )

        result["functions"] = list(functions.values())
        result["categories"] = list(categories.values())
        result["subcategories"] = subcategories

    return result


def transform_800_53_data(data: dict[str, Any]) -> dict[str, Any]:
    """Transform NIST 800-53 Rev. 5 data to our format.

    Expected output structure:
    {
        "framework_id": "nist-800-53-r5",
        "version": "5.1.1",
        "controls": [...]
    }
    """
    result: dict[str, Any] = {
        "framework_id": "nist-800-53-r5",
        "version": "5.1.1",
        "controls": [],
    }

    # Handle different possible response structures
    if "controls" in data:
        result["controls"] = data["controls"]
    elif "elements" in data:
        controls = []
        for elem in data.get("elements", []):
            # Extract family from control ID (e.g., "AC-1" -> "AC")
            ctrl_id = elem.get("element_identifier", "")
            family_id = ctrl_id.split("-")[0] if "-" in ctrl_id else ""

            controls.append(
                {
                    "id": ctrl_id,
                    "name": elem.get("element_name", ctrl_id),
                    "description": elem.get("element_text", ""),
                    "family_id": family_id,
                    "family_name": get_800_53_family_name(family_id),
                    "implementation_examples": elem.get("implementation_examples", []),
                    "informative_references": elem.get("informative_references", []),
                }
            )
        result["controls"] = controls

    return result


def get_800_53_family_name(family_id: str) -> str:
    """Get human-readable family name for 800-53 control family."""
    families = {
        "AC": "Access Control",
        "AT": "Awareness and Training",
        "AU": "Audit and Accountability",
        "CA": "Assessment, Authorization, and Monitoring",
        "CM": "Configuration Management",
        "CP": "Contingency Planning",
        "IA": "Identification and Authentication",
        "IR": "Incident Response",
        "MA": "Maintenance",
        "MP": "Media Protection",
        "PE": "Physical and Environmental Protection",
        "PL": "Planning",
        "PM": "Program Management",
        "PS": "Personnel Security",
        "PT": "PII Processing and Transparency",
        "RA": "Risk Assessment",
        "SA": "System and Services Acquisition",
        "SC": "System and Communications Protection",
        "SI": "System and Information Integrity",
        "SR": "Supply Chain Risk Management",
    }
    return families.get(family_id, family_id)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fetch NIST framework data from CPRT API")
    parser.add_argument(
        "--framework",
        "-f",
        choices=["all", "nist-csf-2.0", "nist-800-53-r5"],
        default="all",
        help="Framework to fetch (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help="Output directory for framework data",
    )

    args = parser.parse_args()

    # Determine output directory
    if args.output_dir is None:
        # Default to data/frameworks relative to project root
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / "data" / "frameworks"
    else:
        output_dir = args.output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which frameworks to fetch
    if args.framework == "all":
        frameworks = ["nist-csf-2.0", "nist-800-53-r5"]
    else:
        frameworks = [args.framework]

    # Fetch each framework
    success = True
    for fw in frameworks:
        if not fetch_framework(fw, output_dir):
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
