# Optional Improvements - Learnings

## SOC 2 TSC 2017 Framework Data File (2026-03-01)

### Task Summary
Created `data/frameworks/soc2-tsc-2017.json` containing SOC 2 Trust Services Criteria (2017) framework data.

### Key Learnings

1. **Framework Data Structure**
   - SOC 2 uses a simpler nested structure than NIST CPRT format
   - Structure: `functions[].categories[].controls[]`
   - FrameworkManager supports this format via the "functions in data" branch (line 294-318 in manager.py)
   - Each control needs: id, name, description, implementation_examples, informative_references

2. **SOC 2 Principle Structure**
   - **CC (Security/Common Criteria)**: Required for all SOC 2 reports; 9 categories (CC1-CC9)
   - **A (Availability)**: Optional; system accessibility and performance
   - **PI (Processing Integrity)**: Optional; data accuracy and processing correctness
   - **C (Confidentiality)**: Optional; protection of sensitive information
   - **P (Privacy)**: Optional; personal information handling
   - CC is always `required: true`; others are `required: false`

3. **Licensing Considerations**
   - SOC 2 is proprietary to AICPA
   - Framework file must include `license_note` explaining this
   - Only use publicly available information (no licensed AICPA content)
   - Implementation examples and informative references can be derived from public sources

4. **Control ID Naming Convention**
   - CC controls: CC1.1, CC1.2, CC1.3, etc.
   - Availability controls: A1.1, A1.2, etc.
   - Processing Integrity: PI1.1, PI1.2, etc.
   - Confidentiality: C1.1, C1.2, etc.
   - Privacy: P1.1, P1.2, etc.

5. **NIST CSF 2.0 Cross-References**
   - CC maps to GV (Govern) and PR (Protect) functions
   - A maps to RC (Recover) and DE (Detect) functions
   - PI maps to PR (Protect) and DE (Detect) functions
   - C maps to PR (Protect) function
   - P maps to GV (Govern) and PR (Protect) functions

### File Statistics
- Total functions: 5
- Total CC categories: 9
- Total CC controls: 27 (3 per category)
- Total A controls: 4
- Total PI controls: 4
- Total C controls: 3
- Total P controls: 8
- All controls have: id, name, description, implementation_examples, informative_references

### Dependencies
- This file is required before FrameworkManager can be updated to load SOC 2
- Mapping file creation (nist-csf-2.0_to_soc2-tsc-2017.json) depends on this file existing

## FrameworkManager SOC2 Support (2026-03-01)

### Task Summary
Updated `src/compliance_oracle/frameworks/manager.py` to support loading the SOC2 framework (`soc2-tsc-2017`).

### Changes Made
1. Added `"soc2-tsc-2017": "soc2-tsc-2017.json"` to `file_map` in `_load_framework()`
2. Added SOC2 entry to `known_frameworks` in `list_frameworks()`
3. Updated `_extract_controls()` to handle both `subcategories` (NIST format) and `controls` (SOC2 format) in nested structure
4. Updated `_count_controls()` to count from both formats

### Key Learnings

1. **Dual Format Support Pattern**
   - Use `or` pattern: `cat.get("subcategories", []) or cat.get("controls", [])`
   - This allows same code path to handle both NIST CSF and SOC2 nested formats
   - NIST CSF: `functions[].categories[].subcategories[]`
   - SOC2: `functions[].categories[].controls[]`

2. **Test Impact**
   - Adding a new framework increases the framework count returned by `list_frameworks()`
   - Tests that hardcode framework counts will need updating
   - 3 tests in `test_frameworks_manager.py` fail due to hardcoded count of 3

3. **Pre-existing Issues**
   - Line 76 has pre-existing mypy error: `Returning Any from function declared to return "dict[str, Any] | None"`
   - This is due to `json.load(f)` returning `Any`
   - Not introduced by this change

### Verification
- `uv run ruff check src/compliance_oracle/frameworks/manager.py` - All checks passed
- `uv run python -c "..."` - Shows all 4 frameworks including soc2-tsc-2017
- 47 tests pass, 3 fail (due to hardcoded framework count)

### Dependencies
- Requires `data/frameworks/soc2-tsc-2017.json` to exist
- Tests in `tests/test_frameworks_manager.py` need count updates (separate task)

## CSF 2.0 to SOC2 Mapping File (2026-03-01)

### Task Summary
Created `data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json` with 35 CSF -> SOC2 mappings and relationship metadata.

### Key Learnings

1. **Mapper Compatibility**
   - `FrameworkMapper._load_mappings()` only requires `source_control_id`, `target_control_id`, and `relationship`
   - Additional fields like names, confidence, and notes are safe and ignored by loader
   - Relationship aliases supported: `equivalent`, `broader`/`superset`, `narrower`/`subset`, `related`

2. **Coverage Strategy That Meets Constraints**
   - Use 35 total mappings to satisfy the 25-35 target while covering all principles
   - Keep CC-heavy distribution (27 mappings) for SOC2 Security depth
   - Include at least 2 mappings each for A, PI, C, and P to avoid principle gaps

3. **Confidence Guardrails**
   - Keep all confidence values <= 0.95 for cross-framework approximation integrity
   - Practical confidence band used: 0.67 to 0.94 based on mapping directness

4. **Quality Verification Pattern**
   - Validate JSON and constraints quickly with `uv run python` and counters
   - Check count, relationship distribution, principle coverage, and confidence bounds in one pass
   - Run LSP diagnostics on the changed JSON file to confirm no editor/schema issues
- Added high-isolation tests for framework_mgmt helper paths by patching module __file__ to redirect data/frameworks writes into pytest tmp_path.
- Coverage target for this module must use --cov=compliance_oracle.tools.framework_mgmt; --cov=src/compliance_oracle/tools/framework_mgmt produces no data.
