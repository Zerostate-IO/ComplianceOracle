# R-013 SOC 2 Implementation - Architectural Decisions

## Decision 1: Hybrid Data Approach

**Decision**: Use a hybrid approach combining community-maintained data with user-provided licensed data.

**Rationale**:
- SOC 2 is proprietary to AICPA; full criteria document requires license
- No public API equivalent to NIST CPRT for SOC 2
- Hybrid approach allows framework to be useful without licensing issues
- Respects AICPA intellectual property rights
- Provides path for licensed users to import complete data

**Alternatives Considered**:
1. **Community-Only**: Use only publicly available information
   - Pro: Simple, no licensing issues
   - Con: Limited usefulness; incomplete coverage
   - Rejected: Too limited for practical use

2. **Licensed-Only**: Require users to provide all SOC 2 data
   - Pro: Complete, accurate data
   - Con: High barrier to entry; not useful without license
   - Rejected: Excludes users without AICPA license

3. **Hybrid** (Selected)
   - Pro: Useful for all users; complete for licensed users; respects IP
   - Con: Requires data import tool; documentation needed
   - Selected: Best balance of usability and compliance

**Implementation**:
- Phase 1: Create community-maintained framework file with public data
- Phase 3: Implement user data import tool for licensed users
- Support merging of community and user-provided data

**Status**: ✅ Decided

---

## Decision 2: No Model Changes Required

**Decision**: Use existing framework-agnostic models; no changes to Control, ControlDetails, or FrameworkInfo schemas.

**Rationale**:
- Existing models are already framework-agnostic
- FrameworkManager and FrameworkMapper support dynamic frameworks
- SOC 2 fits existing data structure without modifications
- Minimizes risk of breaking changes
- Reduces implementation complexity

**Evidence**:
- Control model has `framework_id` field (framework-agnostic)
- FrameworkManager uses file_map for dynamic framework loading
- FrameworkMapper uses generic mapping structure
- No SOC 2-specific fields needed in core models

**Implementation**:
- Update FrameworkManager file_map to include SOC 2
- Create SOC 2 framework JSON following existing structure
- Create SOC 2 mapping JSON following existing format
- No changes to model definitions

**Status**: ✅ Decided

---

## Decision 3: Phased Implementation

**Decision**: Implement SOC 2 support in 4 phases: Framework Structure → Mappings → User Data Import → Documentation.

**Rationale**:
- Allows incremental value delivery
- Reduces risk by validating each phase
- Enables parallel work on documentation
- Provides clear milestones and checkpoints
- Allows deferring optional features (Phase 3)

**Phases**:
1. **Phase 1 (2-3 days)**: Framework structure and loading
2. **Phase 2 (2-3 days)**: Mapping integration and gap analysis
3. **Phase 3 (2-3 days, optional)**: User data import tool
4. **Phase 4 (1-2 days)**: Documentation and user guides

**Benefits**:
- Phase 1 provides basic SOC 2 support
- Phase 2 enables cross-framework analysis
- Phase 3 (optional) enables complete assessment
- Phase 4 ensures users can effectively use SOC 2

**Status**: ✅ Decided

---

## Decision 4: Mapping Confidence Levels

**Decision**: Include confidence levels (0.0-1.0) for each mapping to indicate accuracy and reliability.

**Rationale**:
- SOC 2 and CSF 2.0 have different scopes and purposes
- Mappings based on public guidance may not capture all nuances
- Confidence levels help users understand mapping reliability
- Supports informed decision-making in gap analysis
- Follows best practices for cross-framework mappings

**Confidence Scale**:
- **0.95-1.0**: High confidence (nearly equivalent controls)
- **0.85-0.94**: Good confidence (similar objectives)
- **0.75-0.84**: Moderate confidence (significant overlap)
- **0.65-0.74**: Fair confidence (related but not direct)
- **< 0.65**: Low confidence (limited relationship)

**Implementation**:
- Add `confidence` field to ControlMapping model (if not present)
- Document confidence levels in mapping file
- Provide guidance on interpreting confidence levels
- Use in gap analysis to flag low-confidence mappings

**Status**: ✅ Decided

---

## Decision 5: Licensing Compliance

**Decision**: Use only publicly available information in community-maintained data; do NOT copy licensed AICPA content.

**Rationale**:
- SOC 2 is proprietary to AICPA
- Copying licensed content would violate intellectual property rights
- Using public information is legally safe and ethical
- Respects AICPA's business model
- Allows framework to be distributed freely

**Public Information Sources**:
- AICPA public summaries and overviews
- Audit guidance and best practices
- Published articles and whitepapers
- Industry standards and references
- User-provided licensed data (with permission)

**Implementation**:
- Document license note in framework file
- Include source attribution for all information
- Provide guidance for users with AICPA licenses
- Support user data import for licensed content
- Regular review to ensure compliance

**Status**: ✅ Decided

---

## Decision 6: Framework ID Naming

**Decision**: Use `soc2-tsc-2017` as the framework ID for SOC 2 Trust Services Criteria (2017).

**Rationale**:
- Follows existing naming convention (e.g., `nist-csf-2.0`, `nist-800-53-r5`)
- Includes version number (2017) for clarity
- Includes "tsc" to distinguish from other SOC 2 versions
- Lowercase with hyphens for consistency
- Unambiguous and descriptive

**Alternatives Considered**:
1. `soc2` - Too generic; doesn't specify version
2. `soc2-2017` - Ambiguous; could refer to different criteria
3. `soc2-tsc-2017` (Selected) - Clear, specific, follows convention
4. `aicpa-soc2-tsc-2017` - Too long; redundant

**Usage**:
- Framework ID: `soc2-tsc-2017`
- File: `data/frameworks/soc2-tsc-2017.json`
- Mapping: `nist-csf-2.0_to_soc2-tsc-2017.json`

**Status**: ✅ Decided

---

## Decision 7: Mapping File Location

**Decision**: Store SOC 2 ↔ CSF 2.0 mapping at `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json`.

**Rationale**:
- Follows existing naming convention for mapping files
- Clearly indicates source and target frameworks
- Consistent with existing mappings directory structure
- Supports bidirectional queries (CSF → SOC 2 and SOC 2 → CSF)
- Enables easy discovery and maintenance

**Naming Convention**:
- Format: `{source_framework}_to_{target_framework}.json`
- Example: `nist-csf-2.0_to_soc2-tsc-2017.json`
- Reverse mapping: `soc2-tsc-2017_to_nist-csf-2.0.json` (if needed)

**Status**: ✅ Decided

---

## Decision 8: Documentation Structure

**Decision**: Create 4 separate documentation files for SOC 2 support.

**Rationale**:
- Separates concerns (structure, mapping, implementation, planning)
- Allows targeted reading for different audiences
- Easier to maintain and update
- Follows documentation best practices
- Provides comprehensive coverage

**Files**:
1. **SOC2_FRAMEWORK_STRUCTURE.md** - Framework structure and data models
2. **SOC2_CSF_MAPPING_TEMPLATE.md** - Mapping template and examples
3. **SOC2_IMPLEMENTATION_GUIDE.md** - Step-by-step implementation guide
4. **R-013_SOC2_IMPLEMENTATION_PLAN.md** - Overall implementation plan

**Audience**:
- Framework Structure: Developers, architects
- Mapping Template: Compliance professionals, auditors
- Implementation Guide: Developers implementing SOC 2
- Implementation Plan: Project managers, stakeholders

**Status**: ✅ Decided

---

## Decision 9: Test Coverage Strategy

**Decision**: Add unit tests for SOC 2 framework loading, control retrieval, and mapping integration.

**Rationale**:
- Ensures SOC 2 support works correctly
- Prevents regressions in future changes
- Validates data structure and mappings
- Follows project testing standards
- Supports continuous integration

**Test Coverage**:
- Framework loading and caching
- Control retrieval by function/category
- Mapping loading and relationship types
- Gap analysis with SOC 2
- Bidirectional mapping queries

**Implementation**:
- Add tests to `tests/test_frameworks.py`
- Add tests to `tests/test_mappings.py`
- Aim for 70%+ coverage of SOC 2-related code
- Follow existing test patterns and conventions

**Status**: ✅ Decided

---

## Decision 10: Optional Phase 3 (User Data Import)

**Decision**: Defer user data import tool (Phase 3) to optional enhancement; focus on Phases 1-2 for initial release.

**Rationale**:
- Phases 1-2 provide core SOC 2 support
- Phase 3 is enhancement for licensed users
- Reduces initial implementation scope
- Can be added in future release
- Allows time for community feedback

**Phase 1-2 Deliverables**:
- SOC 2 framework structure
- SOC 2 ↔ CSF 2.0 mappings
- Cross-framework gap analysis
- Basic SOC 2 assessment capability

**Phase 3 (Future)**:
- User data import tool
- Data validation and merging
- Support for complete SOC 2 assessment
- Enhanced guidance for licensed users

**Status**: ✅ Decided

---

## Summary of Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Data Approach | Hybrid (community + user-provided) | Balance usability with licensing compliance |
| Model Changes | None required | Existing models are framework-agnostic |
| Implementation | Phased (4 phases) | Incremental value delivery; reduced risk |
| Mapping Confidence | Include 0.0-1.0 levels | Indicate mapping reliability |
| Licensing | Public information only | Respect AICPA intellectual property |
| Framework ID | `soc2-tsc-2017` | Clear, specific, follows convention |
| Mapping Location | `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json` | Follows existing convention |
| Documentation | 4 separate files | Separates concerns; targeted reading |
| Testing | Unit tests for all phases | Ensures correctness; prevents regressions |
| Phase 3 | Optional; defer to future | Reduces scope; allows community feedback |

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-28  
**Status**: All decisions finalized and documented
