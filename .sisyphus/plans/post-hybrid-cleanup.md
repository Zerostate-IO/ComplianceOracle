# Post-Hybrid Cleanup Stabilization

## TL;DR
> **Summary**: Execute a targeted stabilization pass to clear one failing sanitize test, remove `datetime.utcnow` deprecation usage, and eliminate scoped unused imports introduced in hybrid assessment work.
> **Deliverables**:
> - Correct sanitize test assertion to match policy behavior
> - Replace all identified `datetime.utcnow` usages with timezone-aware UTC patterns
> - Remove scoped unused imports in orchestrator module
> - Verify with targeted checks and full CI-equivalent gate
> **Effort**: Short
> **Parallel**: NO
> **Critical Path**: T1 -> T2 -> T3

## Context
### Original Request
User asked to continue with next steps after Hybrid V1 completion.

### Interview Summary
- User selected **Targeted 3-item** cleanup scope.
- User selected **atomic per-task commits**.
- Cleanup is constrained to stabilization only (no feature expansion).

### Metis Review (gaps addressed)
- Sanitize failure is test/behavior mismatch risk; preserve policy behavior and fix assertion logic.
- `datetime.utcnow` replacements must use timezone-aware UTC, including `default_factory` lambda usage.
- Avoid scope creep into unrelated lint items (e.g., unused local variable) unless explicitly in scope.

## Work Objectives
### Core Objective
Deliver a low-risk cleanup that restores green baseline checks for targeted post-hybrid issues without altering product behavior or expanding scope.

### Deliverables
- Updated sanitize test expectations in `tests/test_assessment.py`.
- Timezone-aware datetime handling in `src/compliance_oracle/documentation/state.py` and `src/compliance_oracle/models/schemas.py`.
- Unused import cleanup in `src/compliance_oracle/assessment/orchestrator.py`.

### Definition of Done (verifiable conditions with commands)
- `uv run pytest tests/test_assessment.py::TestSanitizeText -q` passes.
- `uv run python -W error::DeprecationWarning -c "from compliance_oracle.documentation.state import ComplianceStateManager; from compliance_oracle.models.schemas import ComplianceState; print('ok')"` succeeds.
- `uv run ruff check src/compliance_oracle/assessment/orchestrator.py` passes.
- `uv run ruff check && uv run mypy src/ && uv run pytest` passes.

### Must Have
- Preserve existing no-fix policy behavior; only align tests with intended sanitization semantics.
- Use timezone-aware UTC replacement for all scoped `utcnow` usages.
- Keep cleanup bounded to selected targeted files and symbols.
- Commit each task atomically.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- No changes to remediation policy semantics unless required to satisfy existing tests.
- No broad repository-wide lint/deprecation sweep.
- No feature work, API contract changes, or new dependencies.
- No edits to files outside defined task scope except test fixtures directly needed by scoped tasks.

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification is agent-executed.
- Test decision: tests-after (pytest + ruff + mypy)
- QA policy: Every task includes happy + failure/edge scenario
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`

## Execution Strategy
### Parallel Execution Waves
> Sequential execution selected to minimize regression risk in a small stabilization scope.

Wave 1: Targeted stabilization sequence
- T1 sanitize test alignment
- T2 datetime deprecation replacement
- T3 orchestrator unused import cleanup + full quality gate

### Dependency Matrix (full, all tasks)
| Task | Depends On | Blocks |
|---|---|---|
| T1 | - | T2 |
| T2 | T1 | T3 |
| T3 | T2 | Final Verification |

### Agent Dispatch Summary (wave -> task count -> categories)
- Wave 1 -> 3 tasks -> quick (2), unspecified-low (1)

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.

- [x] T1. Fix sanitize test expectation mismatch in `TestSanitizeText`

  **What to do**: Update `tests/test_assessment.py` sanitize test assertions so they validate current policy behavior (`sanitize_text` replacement output) rather than asserting unchanged input when forbidden recommendation phrases are present.
  **Must NOT do**: Do not change sanitization policy logic in `src/compliance_oracle/assessment/policy.py` unless a failing assertion proves behavior is objectively incorrect against existing test class intent.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: isolated test correction with clear expected behavior.
  - Skills: `[]` — standard pytest/test-editing flow.
  - Omitted: `playwright` — no UI validation.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: T2 | Blocked By: -

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/assessment/policy.py:204` — `sanitize_text` replacement behavior definition.
  - Pattern: `src/compliance_oracle/assessment/policy.py:227` — `enforce_no_fix_policy` output contract.
  - Test: `tests/test_assessment.py:2314` — `TestSanitizeText` class scope.
  - Test: `tests/test_assessment.py:2317` — existing replacement test for "should implement".
  - Test: `tests/test_assessment.py:2326` — failing "we recommend" test.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run pytest tests/test_assessment.py::TestSanitizeText -q` passes.
  - [ ] `uv run pytest tests/test_assessment.py::TestSanitizeText::test_sanitize_replaces_we_recommend -q` passes.
  - [ ] `uv run ruff check tests/test_assessment.py` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: sanitize replacement happy path
    Tool: Bash
    Steps: Run `uv run pytest tests/test_assessment.py::TestSanitizeText::test_sanitize_replaces_we_recommend -q`.
    Expected: Exit code 0; assertion validates replacement output (no forbidden recommendation phrase remains).
    Evidence: .sisyphus/evidence/task-T1-sanitize-happy.txt

  Scenario: regression guard for existing sanitize behavior
    Tool: Bash
    Steps: Run `uv run pytest tests/test_assessment.py::TestSanitizeText::test_sanitize_replaces_should_implement -q`.
    Expected: Exit code 0; existing replacement behavior remains intact.
    Evidence: .sisyphus/evidence/task-T1-sanitize-regression.txt
  ```

  **Commit**: YES | Message: `test(assessment): align sanitize expectations for recommendation phrasing` | Files: `tests/test_assessment.py`

- [x] T2. Replace scoped `datetime.utcnow` with timezone-aware UTC patterns

  **What to do**: Update datetime usage in `src/compliance_oracle/documentation/state.py` and `src/compliance_oracle/models/schemas.py` to timezone-aware UTC (`datetime.now(timezone.utc)`), including `Field(default_factory=...)` usage via lambda where required.
  **Must NOT do**: Do not change timestamp field names, schema shape, or serialization key names.

  **Recommended Agent Profile**:
  - Category: `unspecified-low` — Reason: mechanical deprecation replacement with strict typing impact.
  - Skills: `[]` — straightforward Python refactor.
  - Omitted: `frontend-ui-ux` — backend-only changes.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: T3 | Blocked By: T1

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/documentation/state.py:69` — state update timestamp.
  - Pattern: `src/compliance_oracle/documentation/state.py:98` — document update timestamp.
  - Pattern: `src/compliance_oracle/documentation/state.py:129` — evidence update timestamp.
  - Pattern: `src/compliance_oracle/documentation/state.py:244` — JSON export date.
  - Pattern: `src/compliance_oracle/documentation/state.py:277` — Markdown generated timestamp.
  - Pattern: `src/compliance_oracle/models/schemas.py:175` — `last_updated` default factory.
  - Pattern: `src/compliance_oracle/models/schemas.py:188` — `created_at` default factory.
  - Pattern: `src/compliance_oracle/models/schemas.py:189` — `updated_at` default factory.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run python -W error::DeprecationWarning -c "from compliance_oracle.documentation.state import ComplianceStateManager; from compliance_oracle.models.schemas import ComplianceState; print('ok')"` succeeds.
  - [ ] `uv run pytest tests/test_documentation.py -q` passes.
  - [ ] `uv run mypy src/compliance_oracle/documentation/state.py src/compliance_oracle/models/schemas.py` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: timezone-aware timestamp happy path
    Tool: Bash
    Steps: Run `uv run python -c "from compliance_oracle.models.schemas import ComplianceState; s=ComplianceState(); print(s.created_at.tzinfo)"`.
    Expected: Output indicates UTC tzinfo (not None) and command exits 0.
    Evidence: .sisyphus/evidence/task-T2-datetime-happy.txt

  Scenario: deprecation warning failure guard
    Tool: Bash
    Steps: Run `uv run python -W error::DeprecationWarning -c "from compliance_oracle.documentation.state import ComplianceStateManager; ComplianceStateManager()"`.
    Expected: No DeprecationWarning exception is raised; process exits 0.
    Evidence: .sisyphus/evidence/task-T2-datetime-warning-guard.txt
  ```

  **Commit**: YES | Message: `fix(datetime): replace utcnow with timezone-aware utc timestamps` | Files: `src/compliance_oracle/documentation/state.py`, `src/compliance_oracle/models/schemas.py`

- [x] T3. Remove scoped unused imports and run CI-equivalent quality gate

  **What to do**: Remove targeted unused imports in `src/compliance_oracle/assessment/orchestrator.py` (`Literal`, `PolicyResult`), then run repository quality gate commands (`ruff`, `mypy src/`, full `pytest`) to confirm cleanup is regression-safe.
  **Must NOT do**: Do not expand this task into broad lint cleanup beyond scoped orchestrator import removals.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: narrow code hygiene plus verification execution.
  - Skills: `[]` — standard lint/type/test workflow.
  - Omitted: `dev-browser` — no browser operations.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: Final Verification | Blocked By: T2

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/compliance_oracle/assessment/orchestrator.py:19` — unused `Literal` import.
  - Pattern: `src/compliance_oracle/assessment/orchestrator.py:32` — unused `PolicyResult` import.
  - Pattern: `pyproject.toml:50` — Ruff configuration.
  - Pattern: `pyproject.toml:58` — mypy strict configuration.
  - Pattern: `.github/workflows/ci.yml:30` — lint gate command.
  - Pattern: `.github/workflows/ci.yml:33` — type gate command.
  - Pattern: `.github/workflows/ci.yml:36` — test gate command.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `uv run ruff check src/compliance_oracle/assessment/orchestrator.py` passes.
  - [ ] `uv run ruff check && uv run mypy src/ && uv run pytest` passes.
  - [ ] `uv run pytest tests/test_assessment.py tests/test_tool_contracts.py -q` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```
  Scenario: scoped lint happy path
    Tool: Bash
    Steps: Run `uv run ruff check src/compliance_oracle/assessment/orchestrator.py`.
    Expected: Exit code 0 with no F401 errors for removed imports.
    Evidence: .sisyphus/evidence/task-T3-lint-happy.txt

  Scenario: full-gate regression failure guard
    Tool: Bash
    Steps: Run `uv run ruff check && uv run mypy src/ && uv run pytest`.
    Expected: All commands exit 0; if any fail, task remains incomplete and failures are captured.
    Evidence: .sisyphus/evidence/task-T3-full-gate.txt
  ```

  **Commit**: YES | Message: `chore(assessment): remove unused orchestrator imports and re-verify baseline` | Files: `src/compliance_oracle/assessment/orchestrator.py`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [x] F1. Plan Compliance Audit — oracle
- [x] F2. Code Quality Review — unspecified-high
- [x] F3. Real Manual QA — unspecified-high
- [x] F4. Scope Fidelity Check — deep

## Commit Strategy
- Use atomic commits per task in task order (T1, T2, T3).
- Commit style: conventional commits.
- Planned commit messages:
  - `test(assessment): align sanitize expectations for recommendation phrasing`
  - `fix(datetime): replace utcnow with timezone-aware utc timestamps`
  - `chore(assessment): remove unused orchestrator imports and re-verify baseline`

## Success Criteria
- Targeted cleanup issues are resolved with no behavior regression.
- CI-equivalent local gate (`ruff`, `mypy src/`, full `pytest`) passes.
- Scope remains limited to selected 3-item stabilization work.
