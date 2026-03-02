# Closeout and Stabilization (R-001/R-002)

## TL;DR
> **Summary**: Finish `post-hybrid-cleanup` closeout, then execute a bounded Ruff+mypy stabilization sequence to restore CI-quality baseline without feature work.
> **Deliverables**:
> - F1-F4 closeout completed for `post-hybrid-cleanup`
> - Ruff baseline reduced to zero (`uv run ruff check`)
> - mypy baseline reduced to zero for `src/` (`uv run mypy src/`)
> - Full regression gate green (`uv run pytest`)
> **Effort**: Medium
> **Parallel**: YES - 3 waves
> **Critical Path**: T1 -> T2 -> T3 -> T6 -> T8 -> T9

## Context
### Original Request
User asked what is next and selected: **Close + Stabilize**.

### Interview Summary
- Complete remaining closeout for current cleanup plan.
- Prioritize stabilization before new features.
- Maintain low-risk scope and atomic commits.

### Metis Review (gaps addressed)
- Guardrail added for risky assumptions (B009 autofix behavior, `test_documentation.py` import hotspot, ChromaDB typing drift).
- Explicit acceptance criteria added for F1-F4 and each stabilization cluster.
- Scope creep controls added (no feature work, no blanket ignores, no unsafe Ruff fixes).

## Work Objectives
### Core Objective
Restore trust baseline so local/CI quality checks are truthful and green before roadmap expansion.

### Deliverables
- Verified closeout evidence and checked F1-F4 in `.sisyphus/plans/post-hybrid-cleanup.md`.
- Ruff remediation commits (autofix + manual phases).
- mypy remediation commits (stale ignores + typed mismatches + ChromaDB typing).
- Updated boulder session state for this plan.

### Definition of Done (verifiable conditions with commands)
- `uv run ruff check` exits 0.
- `uv run mypy src/` exits 0.
- `uv run pytest` exits 0.
- `.sisyphus/plans/post-hybrid-cleanup.md` has F1-F4 checked.
- `.sisyphus/boulder.json` points to this plan.

### Must Have
- No `--unsafe-fixes` usage.
- No blanket `# type: ignore` additions.
- Atomic commits per task.
- Tests executed after each high-risk/manual phase.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- No feature/API expansion.
- No broad refactors beyond lint/type fixes.
- No unresolved manual-rule leftovers at plan end.

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification is agent-executed.
- Test decision: tests-after by phase + full final gate.
- QA policy: every task includes happy + failure/edge scenario.
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`.

## Execution Strategy
### Parallel Execution Waves
Wave 1 (closeout + baseline): T1, T2
Wave 2 (Ruff R-001): T3, T4, T5
Wave 3 (mypy R-002 + final gate): T6, T7, T8, T9

### Dependency Matrix (full, all tasks)
| Task | Depends On | Blocks |
|---|---|---|
| T1 | - | T9 |
| T2 | - | T3, T6 |
| T3 | T2 | T4, T5 |
| T4 | T3 | T9 |
| T5 | T3 | T9 |
| T6 | T2 | T7, T8 |
| T7 | T6 | T9 |
| T8 | T6 | T9 |
| T9 | T1, T4, T5, T7, T8 | Final Verification |

### Agent Dispatch Summary (wave -> task count -> categories)
- Wave 1 -> 2 tasks -> quick (1), unspecified-low (1)
- Wave 2 -> 3 tasks -> quick (2), unspecified-high (1)
- Wave 3 -> 4 tasks -> quick (1), unspecified-high (2), deep (1)

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.

- [x] T1. Close `post-hybrid-cleanup` final verification (F1-F4)
  **What to do**: Execute F1-F4 closeout checks and mark them complete in `.sisyphus/plans/post-hybrid-cleanup.md` with evidence artifacts.
  **Must NOT do**: Reopen implementation tasks T1-T3.
  **Recommended Agent Profile**: Category `quick`; Skills `[]`; Omitted `playwright`.
  **Parallelization**: Can Parallel YES | Wave 1 | Blocks T9 | Blocked By -
  **References**: `.sisyphus/plans/post-hybrid-cleanup.md:212`, `.sisyphus/evidence/task-T3-full-gate.txt`
  **Acceptance Criteria**:
  - [ ] F1-F4 are `[x]` in `.sisyphus/plans/post-hybrid-cleanup.md`
  - [ ] Evidence exists for each final verification item
  - [ ] `uv run pytest tests/test_assessment.py tests/test_documentation.py -q` passes
  **QA Scenarios**:
  ```
  Scenario: Closeout happy path
    Tool: Bash
    Steps: Execute closeout checks and update F1-F4.
    Expected: Four checks completed with evidence.
    Evidence: .sisyphus/evidence/task-T1-closeout-happy.txt

  Scenario: Scope guard
    Tool: Bash
    Steps: Inspect diff after closeout.
    Expected: Only post-hybrid plan checkboxes + evidence touched.
    Evidence: .sisyphus/evidence/task-T1-closeout-scope-guard.txt
  ```
  **Commit**: YES | Message: `chore(closeout): complete post-hybrid final verification gate` | Files: `.sisyphus/plans/post-hybrid-cleanup.md`, `.sisyphus/evidence/*`

- [x] T2. Capture Ruff/mypy baseline map
  **What to do**: Run `uv run ruff check` and `uv run mypy src/`, produce deterministic cluster map for remediation order.
  **Must NOT do**: Apply fixes in this task.
  **Recommended Agent Profile**: Category `unspecified-low`; Skills `[]`; Omitted `git-master`.
  **Parallelization**: Can Parallel YES | Wave 1 | Blocks T3,T6 | Blocked By -
  **References**: `pyproject.toml:50`, `pyproject.toml:58`, `.github/workflows/ci.yml:30`, `.github/workflows/ci.yml:33`
  **Acceptance Criteria**:
  - [ ] `.sisyphus/evidence/task-T2-baseline-map.md` exists
  - [ ] Includes rule/error counts by file and remediation waves
  - [ ] Includes timestamp + branch hash
  **QA Scenarios**:
  ```
  Scenario: Baseline happy path
    Tool: Bash
    Steps: Run both commands, summarize outputs.
    Expected: Reproducible map produced.
    Evidence: .sisyphus/evidence/task-T2-baseline-happy.txt

  Scenario: Drift guard
    Tool: Bash
    Steps: Re-run and compare counts.
    Expected: Any drift documented with rationale.
    Evidence: .sisyphus/evidence/task-T2-baseline-drift.txt
  ```
  **Commit**: YES | Message: `docs(stabilization): capture ruff and mypy baseline map` | Files: `.sisyphus/evidence/task-T2-baseline-map.md`

- [x] T3. Apply safe Ruff autofix cluster (R-001 phase A)
  **What to do**: Run safe autofix pass for autofixable rules and verify only manual-rule residuals remain.
  **Must NOT do**: Use `--unsafe-fixes`.
  **Recommended Agent Profile**: Category `quick`; Skills `[]`; Omitted `frontend-ui-ux`.
  **Parallelization**: Can Parallel NO | Wave 2 | Blocks T4,T5 | Blocked By T2
  **References**: `pyproject.toml:54`, `https://docs.astral.sh/ruff/rules/`
  **Acceptance Criteria**:
  - [ ] `uv run ruff check --fix` succeeds
  - [ ] Remaining Ruff output contains only manual categories
  - [ ] `uv run pytest tests/test_assessment.py tests/test_documentation.py -q` passes
  **QA Scenarios**:
  ```
  Scenario: Autofix happy path
    Tool: Bash
    Steps: Run autofix and then check.
    Expected: Autofixable errors removed.
    Evidence: .sisyphus/evidence/task-T3-ruff-autofix-happy.txt

  Scenario: Unsafe-fix guard
    Tool: Bash
    Steps: Verify no unsafe flags used.
    Expected: No `--unsafe-fixes` in evidence/commands.
    Evidence: .sisyphus/evidence/task-T3-ruff-autofix-guard.txt
  ```
  **Commit**: YES | Message: `chore(lint): apply safe ruff autofix baseline` | Files: autofix-touched files only

- [x] T4. Resolve manual Ruff issues in tests
  **What to do**: Fix residual test-only manual rules (E402/SIM117/F841) with minimal structural edits.
  **Must NOT do**: Refactor test architecture.
  **Recommended Agent Profile**: Category `unspecified-high`; Skills `[]`; Omitted `playwright`.
  **Parallelization**: Can Parallel YES | Wave 2 | Blocks T9 | Blocked By T3
  **References**: `tests/test_documentation.py:1121`, `tests/test_assessment.py:1019`
  **Acceptance Criteria**:
  - [ ] `uv run ruff check tests/` passes
  - [ ] `uv run pytest tests/test_documentation.py tests/test_assessment.py -q` passes
  **QA Scenarios**:
  ```
  Scenario: Test lint happy path
    Tool: Bash
    Steps: Run `uv run ruff check tests/`.
    Expected: Exit 0.
    Evidence: .sisyphus/evidence/task-T4-test-lint-happy.txt

  Scenario: Regression guard
    Tool: Bash
    Steps: Run targeted pytest.
    Expected: No behavior regression.
    Evidence: .sisyphus/evidence/task-T4-test-lint-regression.txt
  ```
  **Commit**: YES | Message: `chore(tests): resolve manual ruff findings` | Files: residual test files only

- [x] T5. Resolve manual Ruff issues in `src/` and `scripts/`
  **What to do**: Fix residual source/script manual rules (B904, F841, SIM108).
  **Must NOT do**: Change product behavior except exception chaining clarity.
  **Recommended Agent Profile**: Category `quick`; Skills `[]`; Omitted `dev-browser`.
  **Parallelization**: Can Parallel YES | Wave 2 | Blocks T9 | Blocked By T3
  **References**: `src/compliance_oracle/cli.py:430`, `src/compliance_oracle/assessment/orchestrator.py:225`, `scripts/fetch_nist_data.py:255`
  **Acceptance Criteria**:
  - [ ] `uv run ruff check src/ scripts/` passes
  - [ ] `uv run pytest tests/test_cli.py tests/test_assessment.py -q` passes
  **QA Scenarios**:
  ```
  Scenario: Source lint happy path
    Tool: Bash
    Steps: Run lint on src/scripts.
    Expected: Exit 0.
    Evidence: .sisyphus/evidence/task-T5-src-lint-happy.txt

  Scenario: B904 guard
    Tool: Bash
    Steps: Trigger representative CLI failure path.
    Expected: Exception chaining preserved via `raise ... from exc`.
    Evidence: .sisyphus/evidence/task-T5-src-lint-b904-guard.txt
  ```
  **Commit**: YES | Message: `fix(lint): resolve manual source and script ruff findings` | Files: residual source/script files only

- [x] T6. Remove stale decorator ignores (R-002 phase A)
  **What to do**: Remove stale `type: ignore[untyped-decorator]` comments from tool registration decorators and re-run mypy.
  **Must NOT do**: Remove non-stale ignores unrelated to reported `unused-ignore`.
  **Recommended Agent Profile**: Category `quick`; Skills `[]`; Omitted `git-master`.
  **Parallelization**: Can Parallel NO | Wave 3 | Blocks T7,T8 | Blocked By T2
  **References**: `src/compliance_oracle/tools/lookup.py:16`, `src/compliance_oracle/tools/documentation.py:20`, `src/compliance_oracle/tools/assessment.py:905`, `src/compliance_oracle/tools/framework_mgmt.py:18`
  **Acceptance Criteria**:
  - [ ] `uv run mypy src/` no longer reports stale decorator `unused-ignore`
  - [ ] `uv run pytest tests/test_tool_contracts.py -q` passes
  **QA Scenarios**:
  ```
  Scenario: Ignore cleanup happy path
    Tool: Bash
    Steps: Remove stale ignores; run mypy.
    Expected: Targeted `unused-ignore` diagnostics gone.
    Evidence: .sisyphus/evidence/task-T6-mypy-ignores-happy.txt

  Scenario: Registration guard
    Tool: Bash
    Steps: Import server and list tool registry.
    Expected: Tools still registered.
    Evidence: .sisyphus/evidence/task-T6-mypy-ignores-guard.txt
  ```
  **Commit**: YES | Message: `chore(types): remove stale decorator ignore comments` | Files: `src/compliance_oracle/tools/*.py`

- [x] T7. Fix low-risk mypy mismatches
  **What to do**: Resolve `no-any-return` and non-Chroma arg-type mismatches in framework manager/orchestrator.
  **Must NOT do**: Change assessment semantics.
  **Recommended Agent Profile**: Category `unspecified-high`; Skills `[]`; Omitted `frontend-ui-ux`.
  **Parallelization**: Can Parallel YES | Wave 3 | Blocks T9 | Blocked By T6
  **References**: `src/compliance_oracle/frameworks/manager.py:76`, `src/compliance_oracle/assessment/orchestrator.py:440`, `src/compliance_oracle/assessment/orchestrator.py:545`
  **Acceptance Criteria**:
  - [ ] `uv run mypy src/compliance_oracle/frameworks/manager.py src/compliance_oracle/assessment/orchestrator.py` passes
  - [ ] `uv run pytest tests/test_assessment.py tests/test_frameworks_manager.py -q` passes
  **QA Scenarios**:
  ```
  Scenario: Low-risk typing happy path
    Tool: Bash
    Steps: Run focused mypy.
    Expected: Exit 0 on targeted files.
    Evidence: .sisyphus/evidence/task-T7-mypy-lowrisk-happy.txt

  Scenario: Behavior guard
    Tool: Bash
    Steps: Run representative tests.
    Expected: No behavior regression.
    Evidence: .sisyphus/evidence/task-T7-mypy-lowrisk-guard.txt
  ```
  **Commit**: YES | Message: `fix(types): resolve low-risk mypy mismatches in core modules` | Files: targeted core modules only

- [x] T8. Resolve ChromaDB typing cluster in `rag/search.py`
  **What to do**: Resolve remaining ChromaDB-related mypy errors with precise typing/casts aligned to current API.
  **Must NOT do**: Add blanket file-level ignores.
  **Recommended Agent Profile**: Category `deep`; Skills `[]`; Omitted `playwright`.
  **Parallelization**: Can Parallel YES | Wave 3 | Blocks T9 | Blocked By T6
  **References**: `src/compliance_oracle/rag/search.py:40`, `src/compliance_oracle/rag/search.py:58`, `src/compliance_oracle/rag/search.py:109`, `src/compliance_oracle/rag/search.py:165`, `https://docs.trychroma.com/reference/python/client`
  **Acceptance Criteria**:
  - [ ] `uv run mypy src/compliance_oracle/rag/search.py` passes
  - [ ] `uv run pytest tests/test_rag_search.py -q` passes
  **QA Scenarios**:
  ```
  Scenario: Chroma typing happy path
    Tool: Bash
    Steps: Run focused mypy for `rag/search.py`.
    Expected: No residual Chroma typing errors.
    Evidence: .sisyphus/evidence/task-T8-mypy-chroma-happy.txt

  Scenario: Runtime compatibility guard
    Tool: Bash
    Steps: Instantiate `ControlSearcher` and run targeted tests.
    Expected: Runtime behavior intact.
    Evidence: .sisyphus/evidence/task-T8-mypy-chroma-guard.txt
  ```
  **Commit**: YES | Message: `fix(types): align rag search typing with chromadb api` | Files: `src/compliance_oracle/rag/search.py`

- [x] T9. Final integrated gate + boulder state handoff
  **What to do**: Run integrated quality gate, mark this plan complete, and update `.sisyphus/boulder.json` state.
  **Must NOT do**: Leave unchecked implementation tasks when reporting done.
  **Recommended Agent Profile**: Category `quick`; Skills `[]`; Omitted `dev-browser`.
  **Parallelization**: Can Parallel NO | Wave 3 | Blocks Final Verification | Blocked By T1,T4,T5,T7,T8
  **References**: `.github/workflows/ci.yml:30`, `.github/workflows/ci.yml:33`, `.github/workflows/ci.yml:36`, `.sisyphus/boulder.json`
  **Acceptance Criteria**:
  - [ ] `uv run ruff check && uv run mypy src/ && uv run pytest` passes
  - [ ] T1-T9 checked in this plan
  - [ ] boulder state updated to reflect completion/next active plan
  **QA Scenarios**:
  ```
  Scenario: Final gate happy path
    Tool: Bash
    Steps: Run full gate sequence.
    Expected: All commands exit 0.
    Evidence: .sisyphus/evidence/task-T9-final-gate-happy.txt

  Scenario: State integrity guard
    Tool: Bash
    Steps: Read plan status + boulder state.
    Expected: State coherent, no unchecked implementation tasks.
    Evidence: .sisyphus/evidence/task-T9-final-gate-state.txt
  ```
  **Commit**: YES | Message: `chore(stabilization): finalize quality gates and handoff state` | Files: `.sisyphus/plans/closeout-and-stabilization.md`, `.sisyphus/boulder.json`, `.sisyphus/evidence/*`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
- Keep Ruff autofix commit isolated from manual-lint commits.
- Keep mypy cluster commits isolated (decorator ignores, low-risk types, Chroma cluster).
- Use conventional commit messages.

## Success Criteria
- Post-hybrid cleanup closeout completed and evidenced.
- Ruff and mypy baselines both green.
- Full pytest still green after stabilization.
- No feature scope creep introduced.
