# R-013: SOC 2 Trust Services Principles Framework Support

**Status**: Planning Complete  
**Date**: 2026-02-28  
**Task ID**: R-013  
**Priority**: P2 (Enhancement)  
**Effort**: Medium (M)

## Executive Summary

This document outlines the implementation plan for adding SOC 2 Trust Services Criteria (TSC) support to Compliance Oracle. SOC 2 is a compliance framework developed by the American Institute of Certified Public Accountants (AICPA) for evaluating controls at service organizations.

**Key Challenge**: SOC 2 is a proprietary framework owned by AICPA. Unlike NIST frameworks available via CPRT, SOC 2 requires a license to access the full criteria document.

**Solution**: Implement a hybrid approach combining publicly available SOC 2 information with user-provided licensed data.

## Framework Overview

### SOC 2 Basics

| Aspect | Details |
|--------|---------|
| **Full Name** | Service Organization Control 2 |
| **Owner** | American Institute of Certified Public Accountants (AICPA) |
| **Version** | 2017 Trust Services Criteria (with 2022 Revised Points of Focus) |
| **Scope** | Service organizations providing services to other entities |
| **Principles** | 5 Trust Service Principles (Security, Availability, Processing Integrity, Confidentiality, Privacy) |
| **Controls** | ~100+ detailed control criteria |
| **Audit Types** | Type I (design effectiveness) and Type II (operating effectiveness) |

### Five Trust Service Principles

1. **Security (CC - Common Criteria)** [REQUIRED]
   - Protection against unauthorized access, disclosure, and modification
   - 9 control categories (CC1-CC9)
   - Only required principle for SOC 2 reports

2. **Availability (A)** [OPTIONAL]
   - Information and systems available as committed
   - Addresses business continuity and disaster recovery

3. **Processing Integrity (PI)** [OPTIONAL]
   - Processing is complete, accurate, timely, and authorized
   - Addresses data validation and transaction accuracy

4. **Confidentiality (C)** [OPTIONAL]
   - Confidential information protected against unauthorized disclosure
   - Addresses encryption and access controls

5. **Privacy (P)** [OPTIONAL]
   - Personal information collected, used, retained properly
   - Addresses individual rights and data handling

## Implementation Approach

### Phase 1: Framework Structure (Foundation)

**Objective**: Define SOC 2 framework structure and data models

**Deliverables**:
- SOC 2 framework JSON file with publicly available TSC summaries
- Updated FrameworkManager to load SOC 2
- Unit tests for SOC 2 framework loading

**Effort**: 2-3 days

**Key Files**:
- `data/frameworks/soc2-tsc-2017.json` (new)
- `src/compliance_oracle/frameworks/manager.py` (update)
- `tests/test_frameworks.py` (update)

### Phase 2: Mapping Integration

**Objective**: Integrate SOC 2 ↔ CSF 2.0 mappings

**Deliverables**:
- CSF 2.0 ↔ SOC 2 mapping file with 20-30+ representative mappings
- Updated FrameworkMapper to support SOC 2 mappings
- Unit tests for cross-framework gap analysis

**Effort**: 2-3 days

**Key Files**:
- `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json` (new)
- `src/compliance_oracle/frameworks/mapper.py` (verify/update)
- `tests/test_mappings.py` (update)

### Phase 3: User Data Import (Optional)

**Objective**: Allow users with AICPA licenses to import complete SOC 2 data

**Deliverables**:
- Data import tool for SOC 2 framework data
- CLI command for importing frameworks
- Validation and merging logic

**Effort**: 2-3 days (optional, can be deferred)

**Key Files**:
- `src/compliance_oracle/tools/import_framework.py` (new)
- `src/compliance_oracle/cli.py` (update)

### Phase 4: Documentation & Guidance

**Objective**: Provide comprehensive documentation for SOC 2 support

**Deliverables**:
- SOC 2 framework structure documentation
- CSF 2.0 ↔ SOC 2 mapping template
- SOC 2 implementation guide
- User guide for SOC 2 assessment

**Effort**: 1-2 days

**Key Files**:
- `docs/SOC2_FRAMEWORK_STRUCTURE.md` (new) ✅ COMPLETE
- `docs/SOC2_CSF_MAPPING_TEMPLATE.md` (new) ✅ COMPLETE
- `docs/SOC2_IMPLEMENTATION_GUIDE.md` (new) ✅ COMPLETE
- `README.md` (update)
- `AGENTS.md` (update)

## Data Structure

### SOC 2 Framework JSON

**Location**: `data/frameworks/soc2-tsc-2017.json`

**Structure**:
```json
{
  "framework_id": "soc2-tsc-2017",
  "name": "SOC 2 Trust Services Criteria (2017)",
  "version": "2017",
  "status": "active",
  "description": "AICPA Trust Services Criteria for evaluating controls at service organizations",
  "source_url": "https://www.aicpa.org/soc2",
  "license_note": "SOC 2 is proprietary to AICPA. This file contains publicly available information.",
  "functions": [
    {
      "id": "CC",
      "name": "Security (Common Criteria)",
      "description": "Protection against unauthorized access, disclosure, and modification",
      "required": true,
      "categories": [...]
    },
    {
      "id": "A",
      "name": "Availability",
      "description": "Information and systems are available for operation and use as committed",
      "required": false,
      "categories": [...]
    },
    // ... PI, C, P principles
  ]
}
```

### SOC 2 ↔ CSF 2.0 Mapping

**Location**: `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json`

**Structure**:
```json
{
  "source_framework": "nist-csf-2.0",
  "target_framework": "soc2-tsc-2017",
  "mappings": [
    {
      "source_control_id": "GV.RO-01",
      "target_control_id": "CC1.1",
      "relationship": "equivalent",
      "confidence": 0.95,
      "notes": "Both controls address governance structure"
    }
  ]
}
```

## Mapping Strategy

### Relationship Types

| Type | Definition | Example |
|------|-----------|---------|
| **Equivalent** | Controls address same objective | CSF PR.AC-01 ↔ SOC2 CC6.1 |
| **Broader** | Source covers more than target | CSF PR.DS-01 → SOC2 C1.3 |
| **Narrower** | Source covers part of target | SOC2 CC1.1 ← CSF GV.RO-01 |
| **Related** | Controls overlap but not direct | CSF DE.AE-01 ↔ SOC2 CC5.1 |

### Key Mappings

**Security (CC)**:
- CC1-CC9 map to CSF GV (Govern) and PR (Protect) functions
- Strong overlap with access control and risk management

**Availability (A)**:
- Maps to CSF RC (Recover) and DE (Detect) functions
- Addresses business continuity and disaster recovery

**Processing Integrity (PI)**:
- Maps to CSF PR (Protect) and DE (Detect) functions
- Addresses data accuracy and transaction validation

**Confidentiality (C)**:
- Maps to CSF PR (Protect) function
- Addresses encryption and access controls

**Privacy (P)**:
- Maps to CSF GV (Govern) and PR (Protect) functions
- Addresses personal data handling and individual rights

## Implementation Checklist

### Phase 1: Framework Structure

- [ ] Create `data/frameworks/soc2-tsc-2017.json` with publicly available TSC summaries
- [ ] Update `src/compliance_oracle/frameworks/manager.py` to load SOC 2
- [ ] Add SOC 2 to `list_frameworks()` output
- [ ] Create unit tests for SOC 2 framework loading
- [ ] Verify no ruff or mypy errors
- [ ] Document in `docs/SOC2_FRAMEWORK_STRUCTURE.md` ✅

### Phase 2: Mapping Integration

- [ ] Create `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json` with 20-30+ mappings
- [ ] Verify FrameworkMapper loads SOC 2 mappings
- [ ] Test bidirectional mapping (CSF → SOC 2 and SOC 2 → CSF)
- [ ] Test gap analysis with SOC 2 as target
- [ ] Create unit tests for SOC 2 mappings
- [ ] Verify no ruff or mypy errors
- [ ] Document in `docs/SOC2_CSF_MAPPING_TEMPLATE.md` ✅

### Phase 3: User Data Import (Optional)

- [ ] Create `src/compliance_oracle/tools/import_framework.py`
- [ ] Add `import-framework` CLI command
- [ ] Implement validation and merging logic
- [ ] Create unit tests for data import
- [ ] Document import process

### Phase 4: Documentation & Guidance

- [ ] Update `README.md` to mention SOC 2 support
- [ ] Update `AGENTS.md` with SOC 2 example
- [ ] Create `docs/SOC2_USER_GUIDE.md`
- [ ] Document mapping interpretation
- [ ] Provide example assessment workflows

## Known Limitations

1. **Licensed Content**: SOC 2 is proprietary to AICPA. Initial framework file contains only publicly available information.

2. **Incomplete Coverage**: Without the full AICPA document, initial SOC 2 framework will have limited control details.

3. **User Data Required**: For complete SOC 2 assessment, users must provide their own licensed data.

4. **Mapping Confidence**: Mappings are based on publicly available guidance and may not capture all nuances.

## Data Source Challenge & Solution

### Challenge

SOC 2 is not available via NIST CPRT (unlike NIST CSF 2.0 and NIST 800-53). The full criteria document is proprietary to AICPA and requires a license.

### Solution Options

1. **Community-Maintained Data** (Recommended)
   - Create JSON file with publicly available SOC 2 TSC summaries
   - Include information from AICPA public resources, audit guidance, etc.
   - Do NOT copy licensed content from official AICPA document
   - Allow community contributions and improvements

2. **User-Provided Data**
   - Allow users with AICPA licenses to import their own SOC 2 data
   - Provide data import template and validation schema
   - Support merging with community data

3. **Hybrid Approach** (Recommended)
   - Provide basic framework structure with publicly available information
   - Allow users to enhance with their own licensed data
   - Support merging of community and proprietary data

### Recommended Implementation

Use **Hybrid Approach**:
1. Create community-maintained SOC 2 framework file with publicly available information
2. Implement data import tool for users with AICPA licenses
3. Support merging of community and user-provided data
4. Document licensing requirements and restrictions

## Entry Criteria

✅ **Met**:
- R-006: Add frameworks/manager.py tests (70% coverage) - COMPLETE
- R-007: Add frameworks/mapper.py tests (70% coverage) - COMPLETE

## Exit Criteria

**Phase 1 Complete**:
- SOC 2 framework loads successfully
- SOC 2 appears in framework listings
- SOC 2 controls can be retrieved
- Unit tests pass
- No ruff or mypy errors

**Phase 2 Complete**:
- SOC 2 ↔ CSF 2.0 mappings work correctly
- Gap analysis supports SOC 2
- Bidirectional mappings work
- Unit tests pass
- No ruff or mypy errors

**All Phases Complete**:
- Users can assess SOC 2 compliance
- Users can perform cross-framework gap analysis
- Users can import their own SOC 2 data (Phase 3)
- Comprehensive documentation available

## Timeline Estimate

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1 | 2-3 days | Day 1 | Day 3 |
| Phase 2 | 2-3 days | Day 4 | Day 6 |
| Phase 3 | 2-3 days | Day 7 | Day 9 |
| Phase 4 | 1-2 days | Day 10 | Day 11 |
| **Total** | **7-11 days** | | |

**Note**: Phases can be parallelized. Phase 4 (documentation) can be done concurrently with Phases 1-3.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| AICPA licensing issues | Low | High | Use only publicly available information; document restrictions |
| Incomplete SOC 2 data | Medium | Medium | Provide user data import tool; document limitations |
| Mapping accuracy | Medium | Medium | Use confidence levels; document mapping rationale |
| Integration complexity | Low | Medium | Leverage existing framework infrastructure |

## Success Metrics

1. **Framework Loading**: SOC 2 framework loads without errors
2. **Control Retrieval**: All SOC 2 controls retrievable via API
3. **Mapping Accuracy**: 20-30+ mappings with documented confidence levels
4. **Gap Analysis**: Cross-framework gap analysis works with SOC 2
5. **Test Coverage**: Unit tests for SOC 2 framework and mappings
6. **Documentation**: Comprehensive documentation for users
7. **Code Quality**: No ruff or mypy errors; follows project conventions

## References

### Documentation Created

1. **SOC2_FRAMEWORK_STRUCTURE.md** - Framework structure and data models
2. **SOC2_CSF_MAPPING_TEMPLATE.md** - Mapping template and examples
3. **SOC2_IMPLEMENTATION_GUIDE.md** - Step-by-step implementation guide
4. **R-013_SOC2_IMPLEMENTATION_PLAN.md** - This document

### External References

- **AICPA SOC 2**: https://www.aicpa.org/soc2
- **2017 Trust Services Criteria**: https://www.aicpa.org/ (requires license)
- **NIST CSF 2.0**: https://www.nist.gov/cyberframework
- **SOC 2 Overview**: https://www.aicpa.org/soc2

## Next Steps

1. **Review & Approval**: Review this plan with stakeholders
2. **Phase 1 Implementation**: Create SOC 2 framework structure
3. **Phase 2 Implementation**: Integrate SOC 2 ↔ CSF 2.0 mappings
4. **Phase 3 Implementation** (Optional): Implement user data import
5. **Phase 4 Implementation**: Complete documentation and user guides
6. **Testing & Validation**: Comprehensive testing and validation
7. **Release**: Include SOC 2 support in next release

## Appendix: Quick Reference

### Framework IDs

- **NIST CSF 2.0**: `nist-csf-2.0`
- **NIST 800-53 Rev. 5**: `nist-800-53-r5`
- **SOC 2 TSC 2017**: `soc2-tsc-2017` (new)

### File Locations

- **Framework Data**: `data/frameworks/soc2-tsc-2017.json`
- **Mappings**: `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json`
- **Documentation**: `docs/SOC2_*.md`

### Key Classes

- **FrameworkManager**: Load and query framework data
- **FrameworkMapper**: Map controls across frameworks
- **Control**: Single control in a framework
- **ControlMapping**: Mapping between controls in different frameworks

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-28  
**Author**: Compliance Oracle Team  
**Status**: Ready for Implementation
