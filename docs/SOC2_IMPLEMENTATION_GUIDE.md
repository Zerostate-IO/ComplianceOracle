# SOC 2 Framework Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing SOC 2 Trust Services Criteria (TSC) support in Compliance Oracle. Due to SOC 2 being a proprietary AICPA framework, the implementation uses a hybrid approach combining publicly available information with user-provided licensed data.

## Implementation Phases

### Phase 1: Framework Structure (Foundation)

**Objective**: Define the SOC 2 framework structure and data models

**Tasks**:

1. **Update FrameworkManager** (`src/compliance_oracle/frameworks/manager.py`)
   - Add SOC 2 framework ID mapping: `"soc2-tsc-2017": "soc2-tsc-2017.json"`
   - Update `list_frameworks()` to include SOC 2 metadata
   - Add SOC 2 to known frameworks list

2. **Create SOC 2 Framework Data File** (`data/frameworks/soc2-tsc-2017.json`)
   - Use the structure defined in `SOC2_FRAMEWORK_STRUCTURE.md`
   - Include publicly available TSC summaries
   - Document all 5 principles (CC, A, PI, C, P)
   - Include at least 1-2 example controls per principle

3. **Update Models** (`src/compliance_oracle/models/schemas.py`)
   - Ensure existing `Control`, `ControlDetails`, and `FrameworkInfo` models support SOC 2
   - No changes needed if models are framework-agnostic (they should be)

4. **Testing**
   - Add unit tests for SOC 2 framework loading
   - Test that SOC 2 appears in `list_frameworks()`
   - Test control retrieval for SOC 2

**Deliverable**: SOC 2 framework loads successfully and appears in framework listings

### Phase 2: Mapping Integration

**Objective**: Integrate SOC 2 ↔ CSF 2.0 mappings

**Tasks**:

1. **Create Mapping File** (`data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json`)
   - Use the mapping template from `SOC2_CSF_MAPPING_TEMPLATE.md`
   - Include at least 20-30 representative mappings
   - Cover all 5 SOC 2 principles
   - Assign appropriate confidence levels

2. **Update FrameworkMapper** (`src/compliance_oracle/frameworks/mapper.py`)
   - Ensure mapper can load SOC 2 mappings
   - Test bidirectional mapping (CSF → SOC 2 and SOC 2 → CSF)
   - Verify relationship types are correctly interpreted

3. **Testing**
   - Test mapping retrieval for CSF 2.0 → SOC 2
   - Test mapping retrieval for SOC 2 → CSF 2.0
   - Verify relationship types are preserved
   - Test gap analysis with SOC 2 mappings

**Deliverable**: Cross-framework mappings work correctly; gap analysis supports SOC 2

### Phase 3: User Data Import (Optional Enhancement)

**Objective**: Allow users with AICPA licenses to import complete SOC 2 data

**Tasks**:

1. **Create Data Import Tool** (`src/compliance_oracle/tools/import_framework.py`)
   - Accept JSON file with SOC 2 control data
   - Validate against SOC 2 schema
   - Merge with community data if present
   - Store in `data/frameworks/soc2-tsc-2017-custom.json`

2. **Update CLI** (`src/compliance_oracle/cli.py`)
   - Add `import-framework` command
   - Support `--framework soc2-tsc-2017 --file <path>`
   - Validate imported data

3. **Documentation**
   - Create import template showing expected JSON structure
   - Document validation rules
   - Provide examples

**Deliverable**: Users can import their own SOC 2 data

### Phase 4: Documentation & Guidance

**Objective**: Provide comprehensive documentation for SOC 2 support

**Tasks**:

1. **Update README.md**
   - Add SOC 2 to list of supported frameworks
   - Note that SOC 2 requires user-provided data
   - Link to SOC 2 documentation

2. **Create User Guide** (`docs/SOC2_USER_GUIDE.md`)
   - How to use SOC 2 in Compliance Oracle
   - How to import licensed SOC 2 data
   - Example assessment workflows
   - Mapping interpretation guide

3. **Update AGENTS.md**
   - Add SOC 2 to example agent configuration
   - Show example queries for SOC 2

**Deliverable**: Users can understand and use SOC 2 support

## Data Structure Details

### SOC 2 Framework JSON

**File**: `data/frameworks/soc2-tsc-2017.json`

**Minimum Content**:

```json
{
  "framework_id": "soc2-tsc-2017",
  "name": "SOC 2 Trust Services Criteria (2017)",
  "version": "2017",
  "status": "active",
  "description": "AICPA Trust Services Criteria for evaluating controls at service organizations",
  "source_url": "https://www.aicpa.org/soc2",
  "license_note": "SOC 2 is proprietary to AICPA. This file contains publicly available information. Users must obtain the official criteria from AICPA for complete assessment.",
  "functions": [
    {
      "id": "CC",
      "name": "Security (Common Criteria)",
      "description": "Protection against unauthorized access, disclosure, and modification",
      "required": true,
      "categories": [
        {
          "id": "CC1",
          "name": "Organization and Management",
          "description": "The entity demonstrates a commitment to competence and enforces responsibility for the performance of internal control over the system.",
          "controls": [
            {
              "id": "CC1.1",
              "name": "Governance Structure",
              "description": "The board of directors demonstrates independence from management and exercises oversight of the development, performance, and reporting of internal control over the system.",
              "implementation_examples": [
                "Board charter defining roles and responsibilities",
                "Board meeting minutes documenting oversight activities"
              ],
              "informative_references": [
                "COSO Internal Control Framework",
                "NIST CSF: GV (Governance)"
              ]
            }
          ]
        }
      ]
    },
    {
      "id": "A",
      "name": "Availability",
      "description": "Information and systems are available for operation and use as committed or agreed upon",
      "required": false,
      "categories": []
    },
    {
      "id": "PI",
      "name": "Processing Integrity",
      "description": "System processing is complete, accurate, timely, and authorized",
      "required": false,
      "categories": []
    },
    {
      "id": "C",
      "name": "Confidentiality",
      "description": "Information designated as confidential is protected against unauthorized disclosure",
      "required": false,
      "categories": []
    },
    {
      "id": "P",
      "name": "Privacy",
      "description": "Personal information is collected, used, retained, disclosed, and disposed of to meet the entity's objectives related to privacy",
      "required": false,
      "categories": []
    }
  ]
}
```

### SOC 2 Mapping File

**File**: `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json`

**Structure**:

```json
{
  "source_framework": "nist-csf-2.0",
  "target_framework": "soc2-tsc-2017",
  "version": "1.0",
  "created_date": "2026-02-28",
  "description": "Mapping between NIST CSF 2.0 and SOC 2 Trust Services Criteria",
  "mappings": [
    {
      "source_control_id": "GV.RO-01",
      "source_control_name": "Organizational context and objectives are established and communicated",
      "target_control_id": "CC1.1",
      "target_control_name": "Governance Structure",
      "relationship": "equivalent",
      "confidence": 0.95,
      "notes": "Both controls address governance structure and organizational objectives"
    }
  ]
}
```

## Code Changes Required

### 1. Update FrameworkManager

**File**: `src/compliance_oracle/frameworks/manager.py`

**Changes**:

```python
# In _load_framework method, add to file_map:
file_map = {
    "nist-csf-2.0": "nist-csf-2.0.json",
    "nist-800-53-r5": "nist-800-53-r5.json",
    "soc2-tsc-2017": "soc2-tsc-2017.json",  # ADD THIS
}

# In list_frameworks method, add to known_frameworks:
{
    "id": "soc2-tsc-2017",
    "name": "SOC 2 Trust Services Criteria (2017)",
    "version": "2017",
    "description": "AICPA Trust Services Criteria for evaluating controls at service organizations",
    "source_url": "https://www.aicpa.org/soc2",
},
```

### 2. Update FrameworkMapper

**File**: `src/compliance_oracle/frameworks/mapper.py`

**Changes**: No changes needed if mapper already supports dynamic framework loading

### 3. Update Tests

**File**: `tests/test_frameworks.py`

**Add**:

```python
async def test_soc2_framework_loading():
    """Test that SOC 2 framework loads correctly."""
    manager = FrameworkManager()
    frameworks = await manager.list_frameworks()
    
    soc2 = next((f for f in frameworks if f.id == "soc2-tsc-2017"), None)
    assert soc2 is not None
    assert soc2.name == "SOC 2 Trust Services Criteria (2017)"
    assert soc2.status == FrameworkStatus.ACTIVE

async def test_soc2_controls_retrieval():
    """Test that SOC 2 controls can be retrieved."""
    manager = FrameworkManager()
    controls = await manager.list_controls("soc2-tsc-2017", "CC")
    
    assert len(controls) > 0
    assert all(c.framework_id == "soc2-tsc-2017" for c in controls)

async def test_soc2_csf_mapping():
    """Test mapping between CSF 2.0 and SOC 2."""
    mapper = FrameworkMapper()
    mappings = await mapper.get_mappings("nist-csf-2.0", "soc2-tsc-2017")
    
    assert len(mappings) > 0
    assert all(m.source_framework_id == "nist-csf-2.0" for m in mappings)
    assert all(m.target_framework_id == "soc2-tsc-2017" for m in mappings)
```

## Validation Checklist

Before marking Phase 1 complete:

- [ ] SOC 2 framework file created at `data/frameworks/soc2-tsc-2017.json`
- [ ] FrameworkManager updated to load SOC 2
- [ ] SOC 2 appears in `list_frameworks()` output
- [ ] SOC 2 controls can be retrieved via `list_controls()`
- [ ] Unit tests pass for SOC 2 framework loading
- [ ] No ruff or mypy errors introduced

Before marking Phase 2 complete:

- [ ] Mapping file created at `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json`
- [ ] Mappings load correctly via FrameworkMapper
- [ ] Gap analysis works with SOC 2 as target framework
- [ ] Bidirectional mappings work (CSF → SOC 2 and SOC 2 → CSF)
- [ ] Unit tests pass for SOC 2 mappings
- [ ] No ruff or mypy errors introduced

## Known Limitations

1. **Licensed Content**: SOC 2 is proprietary to AICPA. The initial framework file will contain only publicly available information.

2. **Incomplete Coverage**: Without the full AICPA document, the initial SOC 2 framework will have limited control details.

3. **User Data Required**: For complete SOC 2 assessment, users must provide their own licensed data.

4. **Mapping Confidence**: Mappings between CSF 2.0 and SOC 2 are based on publicly available guidance and may not capture all nuances.

## Future Enhancements

1. **Data Import Tool**: Allow users to import their own SOC 2 data
2. **Enhanced Guidance**: Provide more detailed implementation guidance for SOC 2
3. **Assessment Templates**: Create SOC 2-specific assessment question templates
4. **Audit Report Generation**: Generate SOC 2-specific audit reports
5. **Integration with Other Frameworks**: Add mappings to ISO 27001, HIPAA, etc.

## References

- **SOC 2 Framework Structure**: See `docs/SOC2_FRAMEWORK_STRUCTURE.md`
- **CSF 2.0 ↔ SOC 2 Mapping**: See `docs/SOC2_CSF_MAPPING_TEMPLATE.md`
- **AICPA SOC 2**: https://www.aicpa.org/soc2
- **NIST CSF 2.0**: https://www.nist.gov/cyberframework

## Questions & Support

For questions about SOC 2 implementation:

1. Review the AICPA Trust Services Criteria documentation
2. Consult with your SOC 2 auditor
3. Check the Compliance Oracle documentation
4. Open an issue in the project repository

## License Note

This implementation guide describes how to add SOC 2 support to Compliance Oracle. The SOC 2 Trust Services Criteria are proprietary to AICPA. Users implementing SOC 2 support must:

1. Respect AICPA's intellectual property rights
2. Use only publicly available information in community-maintained data
3. Obtain the official criteria document from AICPA for complete assessment
4. Provide their own licensed data for comprehensive SOC 2 evaluation
