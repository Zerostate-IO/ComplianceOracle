# ComplianceOracle - Linting & Type-Check Baseline Map

**Generated**: 2026-03-02T17:31:07Z
**Git Hash**: a4fbb90173d38d173d070e2f8a6823190c9a220b
**Command Reference**:
- `uv run ruff check`
- `uv run mypy src/`

---

## Executive Summary

| Tool | Total Issues | Autofixable | Manual Fix Required |
|------|-------------|-------------|---------------------|
| **Ruff** | 116 | 105 (91%) | 11 (9%) |
| **mypy** | 31 | N/A | 31 |

**Grand Total**: 147 issues to remediate

---

## Ruff Violations (116 total)

### By Rule

| Rule | Count | Description | Autofix |
|------|-------|-------------|---------|
| F401 | 37 | unused-import | Yes |
| I001 | 25 | unsorted-imports | Yes |
| B009 | 23 | get-attr-with-constant | Yes |
| F811 | 10 | redefined-while-unused | Yes |
| UP017 | 8 | datetime-timezone-utc | Yes |
| E402 | 4 | module-import-not-at-top-of-file | No |
| F841 | 3 | unused-variable | No (unsafe) |
| SIM117 | 2 | multiple-with-statements | No |
| W292 | 2 | missing-newline-at-end-of-file | Yes |
| B904 | 1 | raise-without-from-inside-except | No |
| SIM108 | 1 | if-else-block-instead-of-if-exp | No (unsafe) |

### By File (Top Offenders)

| File | Count | Top Rules |
|------|-------|-----------|
| `tests/test_assessment.py` | 40 | F401 (21), I001 (9), SIM117 (2), F841 (1), W292 (1) |
| `tests/test_documentation.py` | 34 | I001 (15), B009 (9), F811 (6), F401 (2), E402 (2) |
| `src/compliance_oracle/documentation/state.py` | 5 | UP017 (5) |
| `src/compliance_oracle/models/schemas.py` | 3 | UP017 (3) |
| `tests/conftest.py` | 2 | I001 (1), F401 (1) |
| `src/compliance_oracle/cli.py` | 2 | I001 (1), B904 (1) |
| `tests/test_cli.py` | 1 | F401 (1) |
| `src/compliance_oracle/assessment/orchestrator.py` | 1 | F841 (1) |
| `scripts/fetch_nist_data.py` | 1 | SIM108 (1) |

### Full File Breakdown

#### Source Files (src/)

```
src/compliance_oracle/assessment/orchestrator.py
  225:9 F841  Local variable `category` is assigned to but never used

src/compliance_oracle/cli.py
    3:1 I001   Import block is un-sorted or un-formatted
  430:9 B904   raise ... from err (except clause)

src/compliance_oracle/documentation/state.py
   69:47 UP017 Use `datetime.UTC` alias
   98:41 UP017 Use `datetime.UTC` alias
  129:41 UP017 Use `datetime.UTC` alias
  244:41 UP017 Use `datetime.UTC` alias
  277:41 UP017 Use `datetime.UTC` alias

src/compliance_oracle/models/schemas.py
  175:73 UP017 Use `datetime.UTC` alias
  188:71 UP017 Use `datetime.UTC` alias
  189:71 UP017 Use `datetime.UTC` alias
```

#### Test Files (tests/)

```
tests/conftest.py
  3:1  I001 Import block is un-sorted or un-formatted
  5:20 F401 `typing.Any` imported but unused

tests/test_cli.py
  6:8 F401 `pytest` imported but unused

tests/test_documentation.py (34 violations)
  3:22   F401  `datetime.datetime` imported but unused
  367:9  I001  Import block unsorted (x15 occurrences)
  375:28 B009  getattr with constant (x9 occurrences)
  714:13 F811  Redefinition of DegradeReason (x3)
  741:16 F811  Redefinition of json (x3)
  1122:1 E402  Module import not at top (x2)
  1122:27 F811 Redefinition of patch

tests/test_assessment.py (40 violations)
  10:1    I001   Import block unsorted (x9 occurrences)
  1019:9  SIM117 Nested with statements (x2)
  1108:18 F841   Unused variable mock_state_mgr_class
  1562:16 F401   `os` imported but unused
  1674:13 F401   OllamaStatus imported but unused
  1771:16 F401   `httpx` imported but unused (x21 occurrences!)
  3599:55 W292   No newline at end of file
```

---

## mypy Errors (31 total)

### By Error Code

| Code | Count | Description |
|------|-------|-------------|
| unused-ignore | 16 | Stale `# type: ignore` comments |
| valid-type | 2 | ChromaDB type annotation issues |
| attr-defined | 3 | ChromaDB attribute access issues |
| arg-type | 5 | Argument type mismatches |
| no-any-return | 1 | Returning Any from typed function |
| redundant-cast | 2 | Unnecessary int() casts |

### By File

| File | Count | Error Types |
|------|-------|-------------|
| `src/compliance_oracle/rag/search.py` | 12 | valid-type (2), attr-defined (2), arg-type (5), redundant-cast (2) |
| `src/compliance_oracle/tools/framework_mgmt.py` | 4 | unused-ignore (4) |
| `src/compliance_oracle/tools/documentation.py` | 4 | unused-ignore (4) |
| `src/compliance_oracle/tools/lookup.py` | 3 | unused-ignore (3) |
| `src/compliance_oracle/tools/assessment.py` | 3 | unused-ignore (3) |
| `src/compliance_oracle/tools/search.py` | 2 | unused-ignore (2) |
| `src/compliance_oracle/assessment/orchestrator.py` | 2 | arg-type (2) |
| `src/compliance_oracle/frameworks/manager.py` | 1 | no-any-return (1) |

### Full Error Listing

```
src/compliance_oracle/frameworks/manager.py
  76: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]

src/compliance_oracle/tools/lookup.py
  16: error: Unused "type: ignore" comment  [unused-ignore]
  27: error: Unused "type: ignore" comment  [unused-ignore]
  57: error: Unused "type: ignore" comment  [unused-ignore]

src/compliance_oracle/tools/documentation.py
  20: error: Unused "type: ignore" comment  [unused-ignore]
  66: error: Unused "type: ignore" comment  [unused-ignore]
  119: error: Unused "type: ignore" comment  [unused-ignore]
  170: error: Unused "type: ignore" comment  [unused-ignore]

src/compliance_oracle/assessment/orchestrator.py
  440: error: Argument "degrade_reason" incompatible type "DegradeReason | None"; expected "DegradeReason"  [arg-type]
  545: error: Argument "degrade_reason" incompatible type "DegradeReason | None"; expected "DegradeReason"  [arg-type]

src/compliance_oracle/tools/assessment.py
  905: error: Unused "type: ignore" comment  [unused-ignore]
  942: error: Unused "type: ignore" comment  [unused-ignore]
  1046: error: Unused "type: ignore" comment  [unused-ignore]

src/compliance_oracle/rag/search.py (ChromaDB cluster)
  40: error: Function "chromadb.PersistentClient" is not valid as a type  [valid-type]
  43: error: Function "chromadb.PersistentClient" is not valid as a type  [valid-type]
  58: error: chromadb.PersistentClient? has no attribute "get_or_create_collection"  [attr-defined]
  109: error: Argument "metadatas" incompatible type  [arg-type]
  165: error: Argument "where" incompatible type  [arg-type]
  187-190: error: SearchResult field type mismatches (x4)  [arg-type]
  301: error: Redundant cast to "int"  [redundant-cast]
  326: error: Redundant cast to "int"  [redundant-cast]
  328: error: chromadb.PersistentClient? has no attribute "delete_collection"  [attr-defined]

src/compliance_oracle/tools/search.py
  14: error: Unused "type: ignore" comment  [unused-ignore]
  52: error: Unused "type: ignore" comment  [unused-ignore]

src/compliance_oracle/tools/framework_mgmt.py
  18: error: Unused "type: ignore" comment  [unused-ignore]
  52: error: Unused "type: ignore" comment  [unused-ignore]
  87: error: Unused "type: ignore" comment  [unused-ignore]
  137: error: Unused "type: ignore" comment  [unused-ignore]
```

---

## Remediation Waves

### Wave 2A: Ruff Autofixable (105 violations)
**Command**: `uv run ruff check --fix`
**Risk**: Low (safe fixes only)

| Rule | Count | Fix Action |
|------|-------|------------|
| F401 | 37 | Remove unused imports |
| I001 | 25 | Sort imports |
| B009 | 23 | Replace `getattr(x, "const")` with `x.const` |
| F811 | 10 | Remove redefined-unused imports |
| UP017 | 8 | Replace `datetime.timezone.utc` with `datetime.UTC` |
| W292 | 2 | Add trailing newline |

### Wave 2B: Ruff Manual (11 violations)
**Command**: Manual review required

| Rule | Count | Location | Notes |
|------|-------|----------|-------|
| E402 | 4 | test_documentation.py | Move imports to top or add noqa |
| F841 | 3 | orchestrator.py, test_assessment.py | Remove or use variables |
| SIM117 | 2 | test_assessment.py | Combine nested `with` statements |
| B904 | 1 | cli.py:430 | Add `raise ... from err` |
| SIM108 | 1 | scripts/fetch_nist_data.py:255 | Ternary conversion (unsafe autofix) |

### Wave 3A: mypy Stale Ignores (16 violations)
**Action**: Remove unused `# type: ignore` comments

| File | Count | Lines |
|------|-------|-------|
| tools/framework_mgmt.py | 4 | 18, 52, 87, 137 |
| tools/documentation.py | 4 | 20, 66, 119, 170 |
| tools/lookup.py | 3 | 16, 27, 57 |
| tools/assessment.py | 3 | 905, 942, 1046 |
| tools/search.py | 2 | 14, 52 |

### Wave 3B: mypy Low-Risk Fixes (5 violations)
**Action**: Type annotations and casts

| File | Line | Error | Fix |
|------|------|-------|-----|
| frameworks/manager.py | 76 | no-any-return | Add explicit return type cast |
| assessment/orchestrator.py | 440, 545 | arg-type | Guard against None or fix signature |
| rag/search.py | 301, 326 | redundant-cast | Remove unnecessary `int()` casts |

### Wave 3C: mypy ChromaDB Cluster (12 violations)
**Action**: Type stubs or `py.typed` ignore

| File | Error Types | Recommended Fix |
|------|-------------|-----------------|
| rag/search.py:40,43 | valid-type | Use `Client` from `chromadb` or type: ignore |
| rag/search.py:58,328 | attr-defined | Type stubs needed |
| rag/search.py:109,165,187-190 | arg-type | Type annotations for ChromaDB calls |

**Options**:
1. Add `py.typed` ignores for ChromaDB (quick fix)
2. Create local type stubs (proper fix)
3. Migrate to typed alternative

---

## Execution Order Recommendation

```
Phase 1 (Parallel):
  ├── T2A: uv run ruff check --fix          # Wave 2A (105 fixes)
  └── T2B: Manual review Wave 2B            # 11 files

Phase 2 (After Phase 1):
  ├── T3A: Remove stale type: ignore        # Wave 3A (16 fixes)
  └── T3B: Fix low-risk mypy issues         # Wave 3B (5 fixes)

Phase 3 (Optional):
  └── T3C: ChromaDB typing strategy         # Wave 3C (12 fixes)
```

---

## Verification Commands

```bash
# Reproduce this baseline
uv run ruff check --statistics
uv run mypy src/ --no-error-summary 2>&1 | grep -c "error:"

# After Wave 2A
uv run ruff check --statistics  # Should show 11 remaining

# After Wave 3A-3B
uv run mypy src/ 2>&1 | grep -c "error:"  # Should show 12 (ChromaDB only)
```

---

## Notes

1. **Test files dominate**: 74/116 ruff violations are in test files
2. **httpx pattern**: 21 unused `httpx` imports in test_assessment.py suggest test refactoring occurred
3. **ChromaDB typing**: 12 mypy errors stem from untyped third-party library - consider type stubs
4. **Autofix safety**: All 105 autofixable rules have `[*]` marker indicating safe fixes
