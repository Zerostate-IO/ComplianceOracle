---
name: complianceoracle-csf-soc2-mapping-authoring
description: |
  Create and validate `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json` for ComplianceOracle.
  Use when adding SOC2 crosswalks with required constraints: 25-35 mappings, CC-heavy coverage,
  all SOC2 principles represented, valid relationship values, confidence <= 0.95, and JSON validity.
---

# ComplianceOracle CSF->SOC2 Mapping Authoring

## Problem

Authoring SOC2 mapping files can drift from project expectations (wrong field set, weak coverage mix,
or invalid relationship/confidence usage), which breaks consistency and reduces gap-analysis quality.

## Context / Trigger Conditions

- Need to create or update `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json`.
- Requirement includes mapping quality constraints (coverage by principle, confidence bounds, notes).
- Unsure which fields are required by runtime loader versus optional metadata fields.

## Solution

1. Build mappings as CSF source -> SOC2 target using this base schema:
   - Top-level: `source_framework`, `target_framework`, `version`, optional metadata (`created_date`, `description`), `mappings`.
   - Per mapping (minimum): `source_control_id`, `target_control_id`, `relationship`.
   - Recommended extras for explainability: `source_control_name`, `target_control_name`, `confidence`, `notes`.
2. Apply coverage strategy:
   - Total mappings: 25-35.
   - CC principle: 15-20+ preferred for depth.
   - A, PI, C, P: at least 2 mappings each.
3. Apply relationship semantics consistently:
   - `equivalent`: near same objective/scope.
   - `broader`: CSF control covers more than SOC2 target.
   - `narrower`: CSF control covers part of SOC2 target.
   - `related`: overlap but not direct one-to-one.
4. Keep confidence bounded and realistic:
   - Use 0.0-1.0.
   - Keep all values <= 0.95 for approximation integrity.
5. Validate with a quick script:
   - JSON parse success.
   - Count totals and principle distribution.
   - Confirm relationship values and confidence min/max.

## Verification

- Runtime compatibility: `FrameworkMapper._load_mappings()` consumes `source_control_id`, `target_control_id`, and `relationship`; extra fields are tolerated.
- Relationship values are mapped from strings and support aliases (`broader/superset`, `narrower/subset`, etc.).
- JSON parses successfully and satisfies requested mapping/count constraints.

## Example

```json
{
  "source_framework": "nist-csf-2.0",
  "target_framework": "soc2-tsc-2017",
  "version": "1.0",
  "mappings": [
    {
      "source_control_id": "PR.AC-04",
      "target_control_id": "CC6.2",
      "relationship": "equivalent",
      "confidence": 0.92,
      "notes": "Least-privilege authorization aligns with managed user account access controls."
    }
  ]
}
```

## Notes

- The mapping loader ignores metadata fields; include them for human readability and auditability.
- Keep rationale concise in `notes` to support manual review when mapping confidence is not high.
