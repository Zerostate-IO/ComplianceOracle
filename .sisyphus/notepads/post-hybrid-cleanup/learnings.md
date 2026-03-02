# Learnings - Post Hybrid Cleanup

## 2026-03-02: Sanitize Test Fix Pattern

### Context
When fixing tests that validate sanitization/replacement behavior, the test should assert that forbidden content is NOT present in the result, NOT that the result equals the input.

### Pattern
```python
# CORRECT - validates replacement happened
assert "forbidden phrase" not in result.lower()

# INCORRECT - expects no change
assert result == text
```

### Reference
- Test file: tests/test_assessment.py::TestSanitizeText
- Policy file: src/compliance_oracle/assessment/policy.py::_SANITIZATION_REPLACEMENTS

### Key Insight
The sanitize_text function is designed to TRANSFORM text (replace forbidden phrases with neutral language), not preserve it unchanged. Tests should validate the transformation, not the absence of change.


## 2026-03-02: Timezone-Aware datetime.utcnow() Replacement

### Context
When replacing deprecated `datetime.utcnow()` with timezone-aware UTC, special care is needed for Pydantic Field default_factory usage.

### Pattern
```python
# Import - add timezone
from datetime import datetime, timezone

# Regular usage - direct replacement
self._state.updated_at = datetime.now(timezone.utc)

# Pydantic Field - MUST use lambda
class MyModel(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# INCORRECT - captures import-time, not instance-time
created_at: datetime = Field(default_factory=datetime.now(timezone.utc))  # WRONG!
```

### Why Lambda is Required
- `default_factory` expects a callable
- `datetime.now(timezone.utc)` without lambda evaluates immediately at import time
- `lambda: datetime.now(timezone.utc)` defers evaluation to instance creation time

### Files Affected
- src/compliance_oracle/documentation/state.py (5 usages, direct replacement)
- src/compliance_oracle/models/schemas.py (3 usages, lambda required)

### Verification
```bash
uv run python -W error::DeprecationWarning -c "from compliance_oracle.documentation.state import ComplianceStateManager; from compliance_oracle.models.schemas import ComplianceState; print('ok')"
```


## 2026-03-02: Targeted Unused Import Removal

### Context
When removing unused imports from production code, focus on the specific imports identified in the task scope. Pre-existing lint/mypy issues in other files are out of scope.

### Pattern
1. Identify exact line numbers of imports to remove
2. Use Edit tool with precise line replacements
3. Verify only F401 errors for removed imports are fixed
4. Run relevant tests to confirm no regressions

### Task T3 Specifics
- Removed `Literal` from `typing` import (line 19)
- Removed `PolicyResult` from policy import (line 32)
- File: `src/compliance_oracle/assessment/orchestrator.py`

### Scope Discipline
- F841 (unused local variable) errors are OUT OF SCOPE
- Pre-existing mypy errors in other files are OUT OF SCOPE
- Only fix what's explicitly in the task specification

### Verification Commands
```bash
# Verify specific F401 errors are fixed
uv run ruff check src/compliance_oracle/assessment/orchestrator.py --select=F401

# Run relevant tests for regression check
uv run pytest tests/test_assessment.py tests/test_tool_contracts.py -q
```

### Result
- 241 tests passed
- F401 errors for `Literal` and `PolicyResult` eliminated
- Pre-existing F841 and mypy errors remain (out of scope per Metis review)
